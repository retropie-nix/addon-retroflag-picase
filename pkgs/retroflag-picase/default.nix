{
  python3Packages,
  dtc,
}:
let
  inherit (python3Packages)
    rpi-gpio
    setuptools
    setuptools_scm
    buildPythonPackage
    ;
in
buildPythonPackage rec {
  name = "retroflag-picase";
  src = ./.;
  pyproject = true;
  nativeBuildInputs = [ dtc ];
  build-system = [
    setuptools
    setuptools_scm
  ];
  propagatedBuildInputs = [ rpi-gpio ];
  postBuild = ''
    dtc -@ -I dts -O dtb -o RetroFlag_pw_io.dtbo $src/RetroFlag_pw_io.dts
  '';
  postInstall = ''
    install -d $out/share/raspberrypi/boot/overlays
    cp RetroFlag_pw_io.dtbo $out/share/raspberrypi/boot/overlays/RetroFlag_pw_io.dtbo
  '';
}
