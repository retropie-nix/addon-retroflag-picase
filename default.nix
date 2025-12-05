{
  lib,
  system,
  config,
  pkgs,
  options,
  nixos-raspberrypi,
  ...
}:
let
  retroflag-picase = pkgs.callPackage ./pkgs/retroflag-picase { };
in
{
  options = {
    retroflag-picase = {
      enable = lib.mkEnableOption "Retroflag Pi Case Safe Shutdown";
    };
  };
  config = lib.mkIf config.retroflag-picase.enable {
    systemd.services.retroflag-picase = {
      enable = true;
      description = "Retroflag Pi Case Safe Shutdown";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = "${pkgs.retroflag-picase.out}/bin/retroflag-picase";
      };
    };

    nixpkgs = {
      overlays = [
        (_: p: {
          inherit retroflag-picase;
        })
      ];
    };

    boot.loader.raspberryPi.firmwarePackage =
      let
        origfw = nixos-raspberrypi.packages.${pkgs.hostPlatform.system}.raspberrypifw;
      in
      pkgs.symlinkJoin {
        name = origfw.name;
        paths = [
          origfw
          retroflag-picase
        ];
      };

    hardware = {
      raspberry-pi = {
        config = {
          all = {
            options = {
              enable_uart = {
                enable = true;
                value = true;
              };
            };
            dt-overlays = {
              "RetroFlag_pw_io" = {
                enable = true;
                params = { };
              };
            };
          };
        };
      };
    };
  };
}
