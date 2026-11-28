# Security policy

## Reporting a vulnerability

Report a suspected vulnerability privately. **Don't open a public issue,**
because an issue publishes the flaw before there is a fix.

Use GitHub's [private vulnerability reporting][pvr]. Open this repository's
**Security** tab and choose **Report a vulnerability**. That opens an advisory
that only you and the maintainer can see.

Say enough to reproduce it. Give the version or commit you saw it at, the
Home Assistant version, how the Arcana is connected, and what you observed.
Take any encryption key out of a port's URL before you paste it. This is a
small project with no response time promised, but the report will be
acknowledged, you will be kept posted, and the advisory will credit you unless
you ask it not to.

## Which versions get fixes

Only the latest release carries fixes. Report against it or against `main`,
and name the version or the commit.

## What is worth reporting

The integration runs inside Home Assistant with Home Assistant's privileges.
It opens the serial port it is configured with, either a local device such as
`/dev/ttyUSB0` or an `esphome://` URL to an ESPHome serial proxy, and it
speaks the Arcana's text protocol over it.

**It handles an encryption key.** A network port's URL can carry the key of
the proxy's ESPHome API. Anywhere the key reaches a log, a diagnostic, an
entity's state or attributes, or the user interface is worth a report.

**It parses what the device sends.** Every reply from the port becomes an
entity's state. A reply that crashes the integration, stalls Home Assistant's
event loop, or reaches anything other than the state of the entity it answers
for is worth a report.

**It writes to the device.** Entities send settings and commands such as
reboot and factory reset. A way to make the integration send anything other
than the command an entity names is worth a report.

A flaw in Home Assistant itself belongs with [Home Assistant][ha], one in the
serial library with [serialx][serialx], and one in the Arcana's firmware with
[HDFury][hdfury].

[pvr]: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
[ha]: https://www.home-assistant.io/security/
[serialx]: https://github.com/puddly/serialx
[hdfury]: https://www.hdfury.com
