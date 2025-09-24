{
  description = "Disq hybrid development environment (Nix + Docker Compose)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        # Dev shell: reproducible tools
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            docker-compose
            postgresql
            mkcert
            python314
            uv
          ];

          shellHook = ''
            echo "Certs development environment ready!"
            echo ""
            echo "nix run .#up"       # start full stack in Docker
            echo "nix run .#down"     # stop everything

            export upy="uv run python manage.py"

            alias run="$upy runserver"
            alias migrations="$upy makemigrations"
            alias migrate="$upy migrate"
            alias createapp="$upy startapp"
            alias createadmin="$upy createadmin"

            alias docker-migrations="docker compose exec django_backend uv run manage.py makemigrations"
            alias docker-migrate="docker compose exec django_backend uv run manage.py migrate --no-input"
            alias docker-createapp="docker compose exec django_backend uv run manage.py startapp"
            alias docker-createadmin="docker compose exec django_backend uv run manage.py createsuperuser"

            alias docker-clean-all='docker system prune -a -f --volumes'
          '';
        };

        # Shortcuts to run things directly
        apps = {
          # db, cache, frontend
          up = {
            type = "app";
            program = "${pkgs.writeShellScriptBin "up" ''
              docker-compose up
            ''}/bin/up";
          };

          down = {
            type = "app";
            program = "${pkgs.writeShellScriptBin "down" ''
              docker-compose down
            ''}/bin/down";
          };

        };
      });
}
