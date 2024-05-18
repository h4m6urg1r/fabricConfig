{
	pkgs,
	...
}:let
	fabric = pkgs.python3Packages.callPackage ./nix/fabric-meson.nix {};
	package = {
		# lib,
		python3Packages
	}: with python3Packages; buildPythonPackage {
		pname = "testing";
		version = "1.0";

		pyproject = true;
		propagatedBuildInputs = [
			fabric
          python3Packages.psutil
          python3Packages.colorthief
          python3Packages.requests
          python3Packages.lxml
          python3Packages.pam
          python3Packages.thefuzz
		];
        nativeBuildInputs = with pkgs; [
			setuptools
          vala # Vala compiler
          gobject-introspection

          # non python aditional packages
          # gtk-session-lock # For gtk lock screen
          playerctl # For mpirs
          gnome.gnome-bluetooth # For bluetooth
          networkmanager # For network
          libgweather # For weather
          libgudev # For uevent monitoring
		  wrapGAppsHook
        ];

		src = ./test;

		doCheck = false;
	};
in {
	default = pkgs.callPackage package {};
}
