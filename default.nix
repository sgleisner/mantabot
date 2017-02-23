let
  pkgs = import <nixpkgs> {};

  bender = with pkgs.python3Packages; buildPythonPackage rec {
    name = "bender-${version}";
    version = "0.0.3";
    src = pkgs.fetchurl {
   
      url = "https://pypi.python.org/packages/packages/a9/31/9f064b8ecf0da883c2736e96150766c7c1032f095479a7c45f004533a40f/bender-0.0.3.tar.gz";
      md5 = "6218952e92ebffcbc9b5341b70e9155f";
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
     python3Packages.gunicorn
     python3Packages.click
     bender ];
}
