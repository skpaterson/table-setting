pkg_name=table-setting
pkg_origin=habskp
pkg_version="0.1.0"
pkg_maintainer="Stuart Paterson <spaterson@chef.io>"
pkg_license=("Apache-2.0")
pkg_deps=(core/python37)
pkg_lib_dirs=(lib)
pkg_bin_dirs=(bin)
pkg_include_dirs=(include)

do_build() {
  return 0
}

do_install() {
  # install/upgrade pip
  python -m ensurepip --default-pip
  pip install --upgrade pip
  # copy across the one-file table-setting app
  app_dir=$pkg_prefix/$pkg_name
  mkdir $app_dir
  cp run_app.py $app_dir/
  cp requirements.txt $app_dir/
  # create a virtualenv and install dependencies
  python -m venv .
  bin/pip install -r $app_dir/requirements.txt
}