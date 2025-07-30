import React from 'react';
import toast from 'react-hot-toast';

import { sendFetchRequest, getFileBrowsePath } from '@/utils';
import { useCookiesContext } from '@/contexts/CookiesContext';
import type { FileOrFolder } from '@/shared.types';
import { useFileBrowserContext } from '@/contexts/FileBrowserContext';

export default function usePermissionsDialog() {
  const [showAlert, setShowAlert] = React.useState<boolean>(false);
  const { cookies } = useCookiesContext();
  const { currentFileSharePath, refreshFiles } = useFileBrowserContext();

  async function handleChangePermissions(
    targetItem: FileOrFolder,
    localPermissions: FileOrFolder['permissions']
  ) {
    if (!currentFileSharePath) {
      toast.error('No file share path selected.');
      return;
    }

    const fetchPath = getFileBrowsePath(
      currentFileSharePath.name,
      targetItem.path
    );

    try {
      await sendFetchRequest(fetchPath, 'PATCH', cookies['_xsrf'], {
        permissions: localPermissions
      });
      await refreshFiles();
      toast.success(`Successfully updated permissions for ${fetchPath}`);
    } catch (error) {
      toast.error(
        `Error updating permissions for ${fetchPath}: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
    setShowAlert(true);
  }

  return { handleChangePermissions, showAlert, setShowAlert };
}
