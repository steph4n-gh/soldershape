# Local runtime and security reporting

SolderShape is a local research workbench. The service binds to loopback and uses its local request token and request checks. It is not designed as a public multi-user compute service. Do not expose the Python development service through a public tunnel.

Footprints and case files are untrusted input. Archived models and command logs are evidence. Replay regenerates trusted requests from validated inputs and never executes archived scripts. ZIP integrity checks are not an independent signature or a substitute for reviewing the source.

Report vulnerabilities through [GitHub private vulnerability reporting](https://github.com/steph4n-gh/soldershape/security/advisories/new). The repository has private reporting enabled. Include the affected commit, reproduction steps, impact and a minimal shareable input. Do not put exploit details, credentials or confidential boards in public issues.

The research preview has no security response-time or long-term supported-version commitment. The latest research prerelease is the current reporting baseline. Coordinate disclosure privately with the maintainer before publishing details.

The Sites introduction contains recorded examples and static downloads. It does not accept PCB uploads or invoke the local solver. Its access policy is managed separately from the local application.
