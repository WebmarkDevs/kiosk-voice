lk token create \
  --api-key APIMy4Hrt9SMSiF --api-secret MsYEMOefLtK5IPiEKMoBCBBy1HCXf7thtGjkWyOkFCJA \
  --join --room test_room --identity test_user \
  --valid-for 24h

valid for (mins):  1440
Token grants:
{
  "roomJoin": true,
  "room": "test_room"
}

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoibmFtZSIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoibXktcm9vbSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzaXAiOnsiYWRtaW4iOnRydWUsImNhbGwiOnRydWV9LCJzdWIiOiJpZGVudGl0eSIsImlzcyI6IkFQSU15NEhydDlTTVNpRiIsIm5iZiI6MTczMzE1NzYxNSwiZXhwIjoxNzMzMTc5MjE1fQ.K_KIimQxvqwe7XrtJvfVYSWD-eXHacfwOrfObIOPVyk

curl -X POST https://webmark-zkgrasby.livekit.cloud/twirp/livekit.SIP/ListSIPInboundTrunk \
	-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoibmFtZSIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoibXktcm9vbSIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzaXAiOnsiYWRtaW4iOnRydWUsImNhbGwiOnRydWV9LCJzdWIiOiJpZGVudGl0eSIsImlzcyI6IkFQSU15NEhydDlTTVNpRiIsIm5iZiI6MTczMzE1NzYxNSwiZXhwIjoxNzMzMTc5MjE1fQ.K_KIimQxvqwe7XrtJvfVYSWD-eXHacfwOrfObIOPVyk" \
	-H 'Content-Type: application/json' \
	-d '{}'


curl -X POST https://webmark-zkgrasby.livekit.cloud/twirp/livekit.SIP/DeleteSIPTrunk \
	-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoieCIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoieCIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzaXAiOnsiYWRtaW4iOnRydWUsImNhbGwiOnRydWV9LCJzdWIiOiJ4IiwiaXNzIjoiQVBJTXk0SHJ0OVNNU2lGIiwibmJmIjoxNzMzMjE0Nzc3LCJleHAiOjE3MzMyMzYzNzd9.rkoXuu6sJ42kHvOF5LhMcIc0zx58ttvZTMJp5azLqKk" \
	-H 'Content-Type: application/json' \
	-d '{
		"sip_trunk_id": "ST_2TyHV8kPjqyW"
	}'
curl -X POST https://webmark-zkgrasby.livekit.cloud/twirp/livekit.SIP/CreateSIPDispatchRule \
	-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoieCIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoieCIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzaXAiOnsiYWRtaW4iOnRydWUsImNhbGwiOnRydWV9LCJzdWIiOiJ4IiwiaXNzIjoiQVBJTXk0SHJ0OVNNU2lGIiwibmJmIjoxNzMzMjE0Nzc3LCJleHAiOjE3MzMyMzYzNzd9.rkoXuu6sJ42kHvOF5LhMcIc0zx58ttvZTMJp5azLqKk" \
	-H 'Content-Type: application/json' \
	-d '{
		"sip_dispatch_rule_id": "SDR_fYPJxsEuh9M3"
	}'

curl -X POST https://webmark-zkgrasby.livekit.cloud/twirp/livekit.SIP/DeleteSIPDispatchRule \
	-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoieCIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoieCIsImNhblB1Ymxpc2giOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWV9LCJzaXAiOnsiYWRtaW4iOnRydWUsImNhbGwiOnRydWV9LCJzdWIiOiJ4IiwiaXNzIjoiQVBJTXk0SHJ0OVNNU2lGIiwibmJmIjoxNzMzMjE0Nzc3LCJleHAiOjE3MzMyMzYzNzd9.rkoXuu6sJ42kHvOF5LhMcIc0zx58ttvZTMJp5azLqKk" \
	-H 'Content-Type: application/json' \
	-d '{
		"sip_dispatch_rule_id": "SDR_rK5dAXhz7SFq"
	}'