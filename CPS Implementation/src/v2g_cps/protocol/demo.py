from __future__ import annotations

import argparse
import json

from v2g_cps.protocol.scheme import build_default_demo_system


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the secure protocol demo.")
    parser.add_argument("--password", default="correct horse battery staple")
    args = parser.parse_args()

    engine, user, gateway, station = build_default_demo_system()
    trace = engine.authenticate(
        pseudonym=user.pseudonym,
        password=args.password,
        gateway_id=gateway.gateway_id,
        station_id=station.station_id,
    )
    print(json.dumps(trace.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
