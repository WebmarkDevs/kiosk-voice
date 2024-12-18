


wget -qO- https://twilio-cli-prod.s3.amazonaws.com/twilio_pub.asc \
  | sudo apt-key add -
sudo touch /etc/apt/sources.list.d/twilio.list
echo 'deb https://twilio-cli-prod.s3.amazonaws.com/apt/ /' \
  | sudo tee /etc/apt/sources.list.d/twilio.list
sudo apt update
sudo apt install -y twilio

twilio login

twilio api trunking v1 trunks create \
--friendly-name "My test trunk" \
--domain-name "dcdvsvsdvsdnk.pstn.twilio.com"

SID                                 Friendly Name  Domain Name                  
TKdc854fd97a50add432ed9d0a2cc128e4  My test trunk  dcdvsvsdvsdnk.pstn.twilio.com


twilio api trunking v1 trunks origination-urls create \
 --trunk-sid TKdc854fd97a50add432ed9d0a2cc128e4 \
 --friendly-name "LiveKit SIP URI" \
 --sip-url "sip:3bemlrd91yz.sip.livekit.cloud" \
 --weight 1 --priority 1 --enabled

SID                                 Friendly Name    Sip URL                            Priority  Weight
OU1e9fa6b0c66426ad1daefb81dbdc2d8e  LiveKit SIP URI  sip:3bemlrd91yz.sip.livekit.cloud  1         1     
twilio phone-numbers list
PN0feea632059f03e46238e3974ebf71d4  +18159741810  (815) 974-1810
twilio api trunking v1 trunks phone-numbers create \
--trunk-sid TKdc854fd97a50add432ed9d0a2cc128e4 \
--phone-number-sid PN0feea632059f03e46238e3974ebf71d4


twilio api trunking v1 trunks list
lk sip inbound create inbound-trunk.json
SIPTrunkID: ST_BPyENyHDuJ2j
lk sip dispatch create dispatch-rule.json

pip install composio_openai

composio add googlecalendar -e 420a0440-efc1-4a42-94e8-6e63d8d389eb



twilio api trunking v1 trunks phone-numbers remove \
  --trunk-sid TKdc854fd97a50add432ed9d0a2cc128e4 \
  --sid PN25c7f8582428713591f6af04fe3c3247

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