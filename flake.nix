{
  description = "HDFury Arcana Home Assistant custom component";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

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
            pkgs.git
            pkgs.go-task
            pkgs.ruff
          ];

          shellHook = ''
            echo "HDFury Arcana HA development environment loaded!"
            echo "Python: $(python --version)"
          '';
        };
      }
    );
}
