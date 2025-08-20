# MLB Game Records

## What you need

- Elasticsearch cluster (with kibana)
  - [On-Premise in docker](https://www.elastic.co/docs/solutions/search/run-elasticsearch-locally): `curl -fsSL https://elastic.co/start-local | sh`

## Data

Information is pulled via the pybaseball library, using the schedule_and_record CLI.

![Preview of MLB Game Records Dashboard](mlb_game_records.png)
