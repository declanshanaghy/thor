// This example shows how we can format event data ingested through the Ingest REST API's /events endpoint
// into the schema required by a metrics index in SCP. The DSL assumes the following payload was sent to /events:

// [{
// 	 "body": {
// 		 "level": "INFO",
// 		 "time": "2019-01-24T18:06:18.972Z",
// 		 "location": "metrics/metrics.go:206",
// 		 "message": "Http event service metrics",
// 		 "service": "ingest-hec",
// 		 "hostname": "ingest-hec-674bb8496d-djv85",
// 		 "eps": "147.467",
// 		 "records_per_second": "97.90",
// 		 "MBps_read": "0.13",
// 		 "MBps_published": "0.13",
// 		 "totalEventCount": 1407327,
// 		 "totalMB": 1352
// 	 }
// }]

// and formats the data to the following schema required by the metrics index:

// [{
// 	"body": [{
// 		"name": "events_per_second",
// 		"value": 147.467,
// 		"unit": "eps",
// 		"type": ""
// 	}, {
// 		"name": "read_throughput",
// 		"value": 0.13,
// 		"unit": "MBps",
// 		"type": ""
// 	}, {
// 		"name": "write_throughput",
// 		"value": 0.13,
// 		"unit": "MBps",
// 		"type": ""
// 	}, {
// 		"name": "records_per_second",
// 		"value": 97.90,
// 		"unit": "rps",
// 		"type": ""
// 	}],
// 	"source": "metrics/metrics.go:206",
// 	"sourcetype": "scp:ingest",
// 	"attributes": {
// 		"default_dimensions": {
// 			"service": "ingest-hec",
// 			"hostname": "ingest-hec-674bb8496d-djv85"
// 		},
// 		"default_unit": "",
// 		"default_type": ""
// 	},
// 	"timestamp": <timestamp-assigned-by-ingest-API>,
// 	"id": <hash-assigned-by-ingest-API>,
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

write-index(formattedMetrics, module: literal(""), dataset: literal("metrics"));
