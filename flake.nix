{
  description = "HDFury Arcana Home Assistant custom component";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    beads-src = {
      url = "github:steveyegge/beads/v0.62.0";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, beads-src }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        bd = pkgs.buildGoModule {
          pname = "beads";
          version = "0.62.0";
          src = beads-src;
          subPackages = [ "cmd/bd" ];
          vendorHash = "sha256-XGksP4YO2M7nY7g1/ZIN/sprEZLk7i+cdow9uBBcsDo=";
          nativeBuildInputs = [ pkgs.git ];
          doCheck = false;
        };

        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          pyserial-asyncio
          pytest
          pytest-asyncio
          pytest-cov
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            bd
            pkgs.git
            pkgs.ruff
          ];

          shellHook = ''
            echo "HDFury Arcana HA development environment loaded!"
            echo "Python: $(python --version)"
            echo "bd: $(bd --version 2>/dev/null || echo 'available')"
          '';
        };
      }
    );
}
