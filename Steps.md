
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
