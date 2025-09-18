#!/usr/bin/env sh

if [ $# -ne 1 ]; then
  echo "Usage: ${0} uninstall_path"
  echo "  For symmetry with install.sh:"
  echo "    If <uninstall_path> last directory is 'cfgs' ==> <uninstall_path> is deleted"
  echo "    If exists <uninstall_path>/cfgs path ==> <uninstall_path>/cfgs deleted; <uninstall_path> kept"
  echo
  echo "  Some extra safety checks are done to avoid undesired removes."
  exit 1
fi

INSTALL_PATH=${1}

# Test if install_path has some ./cfgs directory
if [ `basename ${INSTALL_PATH}` = "cfgs" ]; then
  LOCAL_CFGS_DIR=${INSTALL_PATH}
else
  LOCAL_CFGS_DIR=${INSTALL_PATH}/cfgs
fi


if [ -d "${LOCAL_CFGS_DIR}" ]; then
  echo "[paraver CFGs] Safety check: ${LOCAL_CFGS_DIR} exist"


  if [ `find ${LOCAL_CFGS_DIR} -name "*.cfg" | wc -l` != "0" ]; then
    echo "[paraver CFGs] Safety check: paraver-cfgs files found."

    if [ -d "${LOCAL_CFGS_DIR}/General" ] &&
       [ -d "${LOCAL_CFGS_DIR}/burst_mode" ] &&
       [ -d "${LOCAL_CFGS_DIR}/spectral" ]; then

      echo "[paraver CFGs] Safety check: paraver-cfgs subdirectories recognized."

      rm -rf ${LOCAL_CFGS_DIR}

      echo "[paraver CFGs] paraver-cfgs uninstalled."

    else
      echo "[paraver CFGs] Safety check FAILED: Unable to recognize paraver-cfgs subdirectories."
      echo "[paraver CFGs] Cowardly rejecting paraver-cfgs remove in ${LOCAL_CFGS_DIR}!!!"
    fi

  else
    echo "[paraver CFGs] Safety check FAILED: Unable to find any .cfg file."
    echo "[paraver CFGs] Cowardly rejecting paraver-cfgs remove in ${LOCAL_CFGS_DIR}!!!"
  fi

else
  echo "[paraver CFGs] Safety check FAILED: Unable to find ${LOCAL_CFGS_DIR} directory."
  echo "[paraver CFGs] Cowardly rejecting paraver-cfgs uninstall in ${LOCAL_CFGS_DIR}!!!"
fi


