{
	pkgs,
	inputs,
	...
}:let
	fabric = pkgs.python3Packages.callPackage ./nix/legacy/fabric.nix { inherit inputs; };
	gir-cvc = pkgs.callPackage ./nix/legacy/gir-cvc.nix {};
	package = {
		# lib,
		python3Packages
	}: with python3Packages; buildPythonPackage {
		pname = "testing";
		version = "1.0";

		pyproject = true;
		propagatedBuildInputs = [
			fabric
			gir-cvc
			psutil
			colorthief
			requests
			lxml
			pam
			thefuzz
			libsass
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
