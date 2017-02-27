let
  pkgs = import <nixpkgs> {};

  bender = with pkgs.python3Packages; buildPythonPackage rec {
    name = "bender-${version}";
    version = "0.0.4";
    src = pkgs.fetchurl {
   
      url = "https://pypi.python.org/packages/b2/03/8667e4de20638bb73eefbdd18c7618a687b4c0d2dc984c130f247bb52fc7/bender-0.0.4.tar.gz";
      md5 = "e6aa60ab6d2d78c6f5e6e3a442233674";
    };
    propagatedBuildInputs = with pkgs;
    [ python3Packages.requests2
      python3Packages.redis
      python3Packages.future ];
    doCheck = false;
  };

in
{ stdenv ? pkgs.stdenv }:

pkgs.python3Packages.buildPythonPackage {
  name = "manta_bot";
  version = "0.1.1";
  src = if pkgs.lib.inNixShell then null else ./.;
  propagatedBuildInputs = with pkgs;
   [ python3
     python3Packages.waitress
     python3Packages.blinker
     python3Packages.flask
     python3Packages.click
     bender ];
}
