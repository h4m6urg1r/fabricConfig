{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
	fabric = {
		url = "github:Fabric-Development/fabric";
		flake = false;
	};
    systems.url = "github:nix-systems/default";
    gtk-session-lock.url = "github:Cu3PO42/gtk-session-lock";
  };

  outputs = {
    systems,
    nixpkgs,
    ...
  } @ inputs: let
    eachSystem = f:
      nixpkgs.lib.genAttrs (import systems) (
        system:
          f (import nixpkgs {
            inherit system;
            overlays = [
              (final: _: let
                gtk-session-lock = inputs.gtk-session-lock.packages.${system}.default;
              in {
                inherit gtk-session-lock;
              })
            ];
          })
      );
	   forAllSystems = nixpkgs.lib.genAttrs [
            "aarch64-linux"
            "i686-linux"
            "x86_64-linux"
            "aarch64-darwin"
            "x86_64-darwin"
        ];
  in {
		packages = forAllSystems (system:
            let pkgs = nixpkgs.legacyPackages.${system};
            in import ./packages.nix { inherit pkgs inputs; }
        );
    devShells = eachSystem (pkgs: let
      fabric = pkgs.python3Packages.callPackage ./nix/legacy/fabric.nix { inputs = inputs; };
	  gir-cvc = pkgs.callPackage ./nix/legacy/gir-cvc.nix {};
    in {
      default = pkgs.mkShell {
        buildInputs = with pkgs; [
          # Custom Packages
          fabric

          # add aditional python packages here
          python3Packages.psutil
          python3Packages.colorthief
          python3Packages.requests
          python3Packages.lxml
          python3Packages.pam
          python3Packages.thefuzz
		  python3Packages.libsass

          ruff # Formatter
          vala-language-server # for vala code completions
        ];
        nativeBuildInputs = with pkgs; [
          vala # Vala compiler
          gobject-introspection
		  gir-cvc

          # non python aditional packages
          gtk-session-lock # For gtk lock screen
          playerctl # For mpirs
          gnome-bluetooth # For bluetooth
          networkmanager # For network
          libgweather # For weather
          libgudev # For uevent monitoring
        ];
      };
    });
  };
}
