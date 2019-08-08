// Format event data into the schema required by a metrics index in SCP.
//
// The DSL assumes the following payload is available in the pipeline:
//
//{
//     "time": 1565213388.534426,
//    "index": "thorevents",
//    "source": "601-Kearney:MainPanel",
//    "event": "site=\"601-Kearney\",
//                node=\"MainPanel\",
//                type=\"voltage\",
//                voltage=116.3"
//}
//{
//    "time": 1565213388.534426,
//    "index": "thorevents",
//    "source": "601-Kearney:MainPanel",
//    "event": "site=\"601-Kearney\",
//                node=\"MainPanel\",
//                type=\"electricity\",
//                name=\"Mains\",
//                channel=24,
//                power=535.0,
//                current=4.3,
//                energy=8.28"
//}
//
// and formats the data to the following schema required by the metrics index:
//
// [{
// 	"body": [{
// 		"name": "voltage",
// 		"value": 147.467,
// 		"unit": "V",
//      "type": "",
// 	}, {
// 		"name": "current",
// 		"value": 0.13,
// 		"unit": "A",
//      "type": "",
//      "channel": 10,
//      "name": "Fridge"
// 	}, {
// 		"name": "power",
// 		"value": 0.13,
// 		"unit": "kW",
//      "type": "",
//      "channel": 10,
//      "name": "Fridge"
// 	}, {
// 		"name": "energy",
// 		"value": 97.90,
// 		"unit": "kWH",
//      "type": "",
//      "channel": 10,
//      "name": "Fridge"
// 	}],
// 	"source": "<site>:<node>",
// 	"attributes": {
// 		"default_dimensions": {
// 			"site": "601-Kearney",
// 			"node": "Main Panel"
// 		},
// 		"default_unit": "",
// 		"default_type": ""
// 	},
// 	"timestamp": "<time>",
// 	"kind": "metric"
// }]

events = read-splunk-firehose();

metrics = list(
    create-map(
        literal("name"), literal("events_per_second"),
        literal("unit"), literal("eps"),
        literal("value"), parse-double(ucast(map-get(ucast(get("body"), "map<string, any>", null), "eps"), "string", null)),
        literal("type"), literal("")
    ),
    create-map(
        literal("name"), literal("read_throughput"),
        literal("unit"), literal("MBps"),
        literal("value"), parse-double(ucast(map-get(ucast(get("body"), "map<string, any>", null), "MBps_read"), "string", null)),
        literal("type"), literal("")
    ),
    create-map(
        literal("name"), literal("write_throughput"),
        literal("unit"), literal("MBps"),
        literal("value"), parse-double(ucast(map-get(ucast(get("body"), "map<string, any>", null), "MBps_published"), "string", null)),
        literal("type"), literal("")
    ),
    create-map(
        literal("name"), literal("records_per_second"),
        literal("unit"), literal("rps"),
        literal("value"), parse-double(ucast(map-get(ucast(get("body"), "map<string, any>", null), "records_per_second"), "string", null)),
        literal("type"), literal("")
    )
);

attributes = create-map(
    literal("default_dimensions"), create-map(
        literal("service"), ucast(map-get(ucast(get("body"), "map<string, any>", null), "service"), "string", null),
        literal("hostname"), ucast(map-get(ucast(get("body"), "map<string, any>", null), "hostname"), "string", null)
    ),
    literal("default_unit"), literal(""),
    literal("default_type"), literal("")
);

formattedMetrics = projection(
    events,
    as(metrics, "body"),
    as("scp:ingest", "source_type"),
    as(ucast(map-get(ucast(get("body"), "map<string, any>", null), "location"), "string", null), "source"),
    as(attributes, "attributes"),
    as(get("timestamp"), "timestamp"),
    as(get("id"), "id"),
    as("metric", "kind")
);

write-index(formattedMetrics, module: literal(""), dataset: literal("thormetricsxformed"));
