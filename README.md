# woodCDN

**Idea**<br />
- Multiple low end servers
- Dashboard to manage vhosts for settings
- Keep the overhead and dependencies at a minimum
- Keep it Simple and Stupid and fucking Dry
- Decentralized + High Availability even if the db cluster shits itself, stuff should keep going
- GeoDNS to reduce latency

**Software**<br />
- Nginx as proxy/caching device
- rqlited to store the vhosts
- python3 for syncing/generating the vhosts
- python3 to add/edit/delete vhosts and settings
