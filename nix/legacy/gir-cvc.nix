{
  stdenv,
  fetchurl,
  lib,
  pkg-config,
  gobject-introspection,
  meson,
  ninja,
  cmake,
  gdk-pixbuf,
  gtk3,
  systemd,
  xkeyboard_config,
  libxkbfile,
  libpulseaudio,
}:
stdenv.mkDerivation (finalAttrs: {
  pname = "libcvc-gir";
  # random version lol
  version = "22.0";

  src = fetchurl {
    url = "https://github.com/linuxmint/cinnamon-desktop/archive/refs/tags/master.mint22.tar.gz";
    hash = "sha256-cnUZ0SMJmJsq/jgu4s1HJaIo9Osm5S28aQ8FwdofSuE=";
  };

  nativeBuildInputs = [meson ninja pkg-config gobject-introspection];

  # unsure if this patch actually gets applied
  patches = [
    ./meson.build.patch
  ];

  buildInputs = [
	cmake
	systemd
	xkeyboard_config
	libxkbfile
    gdk-pixbuf
    gtk3
    libpulseaudio
  ];

  doCheck = false;
})
