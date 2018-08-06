pkg_name=table-setting
pkg_origin=habskp
pkg_version="0.1.0"
pkg_maintainer="Stuart Paterson <spaterson@chef.io>"
pkg_license=("Apache-2.0")
pkg_deps=(core/python37 core/mysql-client core/gcc)
pkg_lib_dirs=(lib)
pkg_bin_dirs=(bin)
pkg_include_dirs=(include)

pkg_binds_optional=(
  [database]="port password username"
)

do_build() {
  return 0
}

do_install() {
  # copy across the one-file table-setting app plus requirements
  app_dir=$pkg_prefix/$pkg_name
  mkdir $app_dir
  cp run_app.py $app_dir/
  cp requirements.txt $app_dir/
  #install pip/virtualenv packages on top of python dependency (i.e. site packages)
  pip install --upgrade pip
  pip install virtualenv
  # create virtualenv for our dependencies & install
  virtualenv $app_dir/tsenv
  source $app_dir/tsenv/bin/activate
  pip install -r $app_dir/requirements.txt
  # explicitly deal with the more complicated dependency for mysql here
  pip install mysqlclient
  # ensure hab user can activate the virtualenv
  chown -R hab:hab $app_dir
}