// Format event data into the schema required by a metrics index in SCP.
//
// The DSL assumes the following payloads are available from the LSDC events:
//
//{
//    "time": 1565213388.534426,
//    "index": "thorevents",
//    "source": "601-Kearney:MainPanel",
//    "event": "site=\"601-Kearney\",
//              node=\"MainPanel\",
//              type=\"voltage\",
//              voltage=116.3"
//}
//{
//    "time": 1565213388.534426,
//    "index": "thorevents",
//    "source": "601-Kearney:MainPanel",
//    "event": "site=\"601-Kearney\",
//              node=\"MainPanel\",
//              type=\"temperature\",
//              name=\"Garage\",
//              temperature=74.0"}
//{
//    "time": 1565213388.534426,
//    "index": "thorevents",
//    "source": "601-Kearney:MainPanel",
//    "event": "site=\"601-Kearney\",
//              node=\"MainPanel\",
//              type=\"electricity\",
//              name=\"Mains\",
//              channel=24,
//              power=535.0,
//              current=4.3,
//              energy=8.28"
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

//events = read-splunk-firehose();
events = read-from-aws-s3(connection-id: literal("531631d0-b1cf-4c70-b512-09afc1838258"));


metrics = list(
//    create-map(
//        literal("name"), literal("voltage"),
//        literal("unit"), literal("v"),
//        literal("type"), literal(""),
//        literal("value"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "voltage"), "string", null)),
//        literal("channel"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "channel"), "string", null)),
//        literal("name"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "name"), "string", null))
//    ),
    create-map(
        literal("name"), literal("current"),
        literal("unit"), literal("A"),
        literal("type"), literal(""),
        literal("value"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "current"), "string", null)),
        literal("channel"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "channel"), "string", null)),
        literal("name"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "name"), "string", null))
    ),
    create-map(
        literal("name"), literal("power"),
        literal("unit"), literal("kW"),
        literal("type"), literal(""),
        literal("value"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "power"), "string", null)),
        literal("channel"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "channel"), "string", null)),
        literal("name"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "name"), "string", null))
    ),
    create-map(
        literal("name"), literal("energy"),
        literal("unit"), literal("kWh"),
        literal("type"), literal(""),
        literal("value"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "energy"), "string", null)),
        literal("channel"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "channel"), "string", null)),
        literal("name"), parse-double(ucast(map-get(ucast(get("event"), "map<string, any>", null), "name"), "string", null))
    )
);

attributes = create-map(
    literal("default_dimensions"), create-map(
        literal("site"), ucast(map-get(ucast(get("event"), "map<string, any>", null), "site"), "string", null),
        literal("node"), ucast(map-get(ucast(get("event"), "map<string, any>", null), "node"), "string", null)
    ),
    literal("default_unit"), literal(""),
    literal("default_type"), literal("")
);

formattedMetrics = projection(
    events,
    as(get("timestamp"), "timestamp"),
    as(metrics, "body"),
    as("gem:electricity", "source_type"),
    as("601-Kearney:MainPanel", "source"),
    as(attributes, "attributes"),
    as("metric", "kind")
);

write-index(formattedMetrics, module: literal(""), dataset: literal("thormetricsxformed"));

