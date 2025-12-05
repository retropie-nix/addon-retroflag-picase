rec {
  description = "Retroflag Pi Case addon for retropie-nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  nixConfig = {
    extra-experimental-features = [
      "nix-command"
      "flakes"
    ];
    extra-substituters = [
      "https://nix-community.cachix.org"
      "https://nixos-raspberrypi.cachix.org"
    ];
    extra-trusted-public-keys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
      "nixos-raspberrypi.cachix.org-1:4iMO9LXa8BqhU+Rpg6LQKiGa2lsNh/j2oiYLNOQ5sPI="
    ];
  };

  outputs = { flake-utils, ... }: flake-utils.lib.eachSystemPassThrough [ "aarch64-linux" ] (system: {
    nixosModules.default = import ./.;
  });
}
