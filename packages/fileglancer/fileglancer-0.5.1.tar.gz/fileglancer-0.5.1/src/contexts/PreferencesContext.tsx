import React from 'react';
import { default as log } from '@/logger';

import type { FileSharePath, Zone } from '@/shared.types';
import { useCookiesContext } from '@/contexts/CookiesContext';
import { useZoneAndFspMapContext } from './ZonesAndFspMapContext';
import { useOpenFavoritesContext } from './OpenFavoritesContext';
import { sendFetchRequest, makeMapKey, HTTPError } from '@/utils';

export type FolderFavorite = {
  type: 'folder';
  folderPath: string;
  fsp: FileSharePath;
};

// Types for the zone, fsp, and folder information stored to the backend "preferences"
export type ZonePreference = { type: 'zone'; name: string };
export type FileSharePathPreference = { type: 'fsp'; name: string };
export type FolderPreference = {
  type: 'folder';
  folderPath: string;
  fspName: string;
};

type PreferencesContextType = {
  pathPreference: ['linux_path'] | ['windows_path'] | ['mac_path'];
  showPathPrefAlert: boolean;
  setShowPathPrefAlert: React.Dispatch<React.SetStateAction<boolean>>;
  handlePathPreferenceSubmit: (
    event: React.FormEvent<HTMLFormElement>,
    localPathPreference: PreferencesContextType['pathPreference']
  ) => void;
  zonePreferenceMap: Record<string, ZonePreference>;
  zoneFavorites: Zone[];
  fileSharePathPreferenceMap: Record<string, FileSharePathPreference>;
  fileSharePathFavorites: FileSharePath[];
  folderPreferenceMap: Record<string, FolderPreference>;
  folderFavorites: FolderFavorite[];
  isFileSharePathFavoritesReady: boolean;
  handleFavoriteChange: (
    item: Zone | FileSharePath | FolderFavorite,
    type: 'zone' | 'fileSharePath' | 'folder'
  ) => Promise<void>;
};

const PreferencesContext = React.createContext<PreferencesContextType | null>(
  null
);

export const usePreferencesContext = () => {
  const context = React.useContext(PreferencesContext);
  if (!context) {
    throw new Error(
      'usePreferencesContext must be used within a PreferencesProvider'
    );
  }
  return context;
};

export const PreferencesProvider = ({
  children
}: {
  children: React.ReactNode;
}) => {
  const [pathPreference, setPathPreference] = React.useState<
    ['linux_path'] | ['windows_path'] | ['mac_path']
  >(['linux_path']);
  const [showPathPrefAlert, setShowPathPrefAlert] = React.useState(false);

  const [zonePreferenceMap, setZonePreferenceMap] = React.useState<
    Record<string, ZonePreference>
  >({});
  const [zoneFavorites, setZoneFavorites] = React.useState<Zone[]>([]);
  const [fileSharePathPreferenceMap, setFileSharePathPreferenceMap] =
    React.useState<Record<string, FileSharePathPreference>>({});
  const [fileSharePathFavorites, setFileSharePathFavorites] = React.useState<
    FileSharePath[]
  >([]);
  const [folderPreferenceMap, setFolderPreferenceMap] = React.useState<
    Record<string, FolderPreference>
  >({});
  const [folderFavorites, setFolderFavorites] = React.useState<
    FolderFavorite[]
  >([]);
  const [isFileSharePathFavoritesReady, setIsFileSharePathFavoritesReady] =
    React.useState(false);

  const { cookies } = useCookiesContext();
  const { isZonesMapReady, zonesAndFileSharePathsMap } =
    useZoneAndFspMapContext();
  const { openFavoritesSection } = useOpenFavoritesContext();

  const fetchPreferences = React.useCallback(
    async (key: string) => {
      try {
        const data = await sendFetchRequest(
          `/api/fileglancer/preference?key=${key}`,
          'GET',
          cookies['_xsrf']
        ).then(response => response.json());
        return data?.value;
      } catch (error) {
        if (error instanceof HTTPError && error.responseCode === 404) {
          log.debug(`Preference '${key}' not found`);
        } else {
          log.error(`Error fetching preference '${key}':`, error);
        }
        return null;
      }
    },
    [cookies]
  );

  const accessMapItems = React.useCallback(
    (keys: string[]) => {
      const itemsArray = keys.map(key => {
        return zonesAndFileSharePathsMap[key];
      });
      // To help with debugging edge cases
      log.debug(`length of preference keys list: ${keys.length}`);
      log.debug(`length of accessed items list: ${itemsArray.length}`);
      return itemsArray;
    },
    [zonesAndFileSharePathsMap]
  );

  const updateLocalZonePreferenceStates = React.useCallback(
    (updatedMap: Record<string, ZonePreference>) => {
      setZonePreferenceMap(updatedMap);
      const updatedZoneFavorites = accessMapItems(
        Object.keys(updatedMap)
      ) as Zone[];
      updatedZoneFavorites.sort((a, b) => a.name.localeCompare(b.name));
      setZoneFavorites(updatedZoneFavorites as Zone[]);
    },
    [accessMapItems]
  );

  const updateLocalFspPreferenceStates = React.useCallback(
    (updatedMap: Record<string, FileSharePathPreference>) => {
      setFileSharePathPreferenceMap(updatedMap);
      const updatedFspFavorites = accessMapItems(
        Object.keys(updatedMap)
      ) as FileSharePath[];
      // Sort based on the storage name, which is what is displayed in the UI
      updatedFspFavorites.sort((a, b) => a.storage.localeCompare(b.storage));
      setFileSharePathFavorites(updatedFspFavorites as FileSharePath[]);
      setIsFileSharePathFavoritesReady(true);
    },
    [accessMapItems]
  );

  const updateLocalFolderPreferenceStates = React.useCallback(
    (updatedMap: Record<string, FolderPreference>) => {
      setFolderPreferenceMap(updatedMap);
      const updatedFolderFavorites = Object.entries(updatedMap).map(
        ([_, value]) => {
          const fspKey = makeMapKey('fsp', value.fspName);
          const fsp = zonesAndFileSharePathsMap[fspKey];
          return { type: 'folder', folderPath: value.folderPath, fsp: fsp };
        }
      );
      // Sort by the last segment of folderPath, which is the folder name
      updatedFolderFavorites.sort((a, b) => {
        const aLastSegment = a.folderPath.split('/').pop() || '';
        const bLastSegment = b.folderPath.split('/').pop() || '';
        return aLastSegment.localeCompare(bLastSegment);
      });
      setFolderFavorites(updatedFolderFavorites as FolderFavorite[]);
    },
    [zonesAndFileSharePathsMap]
  );

  const savePreferencesToBackend = React.useCallback(
    async <T,>(key: string, value: T) => {
      try {
        await sendFetchRequest(
          `/api/fileglancer/preference?key=${key}`,
          'PUT',
          cookies['_xsrf'],
          { value: value }
        );
      } catch (error) {
        console.error(`Error updating preference '${key}':`, error);
      }
    },
    [cookies]
  );

  const handlePathPreferenceSubmit = React.useCallback(
    (
      event: React.FormEvent<HTMLFormElement>,
      localPathPreference: ['linux_path'] | ['windows_path'] | ['mac_path']
    ) => {
      event.preventDefault();
      try {
        savePreferencesToBackend('path', localPathPreference);
        setPathPreference(localPathPreference);
        setShowPathPrefAlert(true);
      } catch (error) {
        console.error('Error in handlePathPreferenceSubmit:', error);
        setShowPathPrefAlert(false);
      }
    },
    [savePreferencesToBackend]
  );

  function updatePreferenceList<T>(
    key: string,
    itemToUpdate: T,
    favoritesList: Record<string, T>
  ): { updatedFavorites: Record<string, T>; favoriteAdded: boolean } {
    const updatedFavorites = { ...favoritesList };
    const match = updatedFavorites[key];
    let favoriteAdded = false;
    if (match) {
      delete updatedFavorites[key];
      favoriteAdded = false;
    } else if (!match) {
      updatedFavorites[key] = itemToUpdate;
      favoriteAdded = true;
    }
    return { updatedFavorites, favoriteAdded };
  }

  const handleZoneFavoriteChange = React.useCallback(
    async (item: Zone) => {
      try {
        const key = makeMapKey('zone', item.name);
        const { updatedFavorites, favoriteAdded } = updatePreferenceList(
          key,
          { type: 'zone', name: item.name },
          zonePreferenceMap
        ) as {
          updatedFavorites: Record<string, ZonePreference>;
          favoriteAdded: boolean;
        };
        await savePreferencesToBackend('zone', Object.values(updatedFavorites));
        updateLocalZonePreferenceStates(updatedFavorites);
        return favoriteAdded;
      } catch (error) {
        console.error('Error in handleZoneFavoriteChange:', error);
      }
    },
    [
      zonePreferenceMap,
      savePreferencesToBackend,
      updateLocalZonePreferenceStates
    ]
  );

  const handleFileSharePathFavoriteChange = React.useCallback(
    async (item: FileSharePath) => {
      try {
        const key = makeMapKey('fsp', item.name);
        const { updatedFavorites, favoriteAdded } = updatePreferenceList(
          key,
          { type: 'fsp', name: item.name },
          fileSharePathPreferenceMap
        ) as {
          updatedFavorites: Record<string, FileSharePathPreference>;
          favoriteAdded: boolean;
        };
        await savePreferencesToBackend(
          'fileSharePath',
          Object.values(updatedFavorites)
        );
        updateLocalFspPreferenceStates(updatedFavorites);
        return favoriteAdded;
      } catch (error) {
        console.error('Error in handleFileSharePathFavoriteChange:', error);
      }
    },
    [
      fileSharePathPreferenceMap,
      savePreferencesToBackend,
      updateLocalFspPreferenceStates
    ]
  );

  const handleFolderFavoriteChange = React.useCallback(
    async (item: FolderFavorite) => {
      try {
        const folderPrefKey = makeMapKey(
          'folder',
          `${item.fsp.name}_${item.folderPath}`
        );
        const { updatedFavorites, favoriteAdded } = updatePreferenceList(
          folderPrefKey,
          {
            type: 'folder',
            folderPath: item.folderPath,
            fspName: item.fsp.name
          },
          folderPreferenceMap
        ) as {
          updatedFavorites: Record<string, FolderPreference>;
          favoriteAdded: boolean;
        };
        await savePreferencesToBackend(
          'folder',
          Object.values(updatedFavorites)
        );
        updateLocalFolderPreferenceStates(updatedFavorites);
        return favoriteAdded;
      } catch (error) {
        console.error('Error in handleFolderFavoriteChange:', error);
      }
    },
    [
      folderPreferenceMap,
      savePreferencesToBackend,
      updateLocalFolderPreferenceStates
    ]
  );

  const handleFavoriteChange = React.useCallback(
    async (
      item: Zone | FileSharePath | FolderFavorite,
      type: 'zone' | 'fileSharePath' | 'folder'
    ) => {
      let favoriteAdded = false;
      try {
        switch (type) {
          case 'zone':
            favoriteAdded = (await handleZoneFavoriteChange(
              item as Zone
            )) as boolean;
            break;
          case 'fileSharePath':
            favoriteAdded = (await handleFileSharePathFavoriteChange(
              item as FileSharePath
            )) as boolean;
            break;
          case 'folder':
            favoriteAdded = (await handleFolderFavoriteChange(
              item as FolderFavorite
            )) as boolean;
            break;
          default:
            throw new Error(`Invalid type: ${type}`);
        }
      } catch (error) {
        log.error('Error in handleFavoriteChange:', error);
      }
      if (favoriteAdded) {
        openFavoritesSection();
      }
    },
    [
      handleZoneFavoriteChange,
      handleFileSharePathFavoriteChange,
      handleFolderFavoriteChange,
      openFavoritesSection
    ]
  );

  React.useEffect(() => {
    (async function () {
      const rawPathPreference = await fetchPreferences('path');
      if (rawPathPreference) {
        log.debug('setting initial path preference:', rawPathPreference);
        setPathPreference(rawPathPreference);
      }
    })();
  }, [fetchPreferences]);

  React.useEffect(() => {
    if (!isZonesMapReady) {
      return;
    }

    (async function () {
      const backendPrefs = await fetchPreferences('zone');
      const zoneArray =
        backendPrefs?.map((pref: ZonePreference) => {
          const key = makeMapKey(pref.type, pref.name);
          return { [key]: pref };
        }) || [];
      const zoneMap = Object.assign({}, ...zoneArray);
      if (zoneMap) {
        updateLocalZonePreferenceStates(zoneMap);
      }
    })();
  }, [isZonesMapReady, fetchPreferences, updateLocalZonePreferenceStates]);

  React.useEffect(() => {
    if (!isZonesMapReady) {
      return;
    }

    (async function () {
      const backendPrefs = await fetchPreferences('fileSharePath');
      const fspArray =
        backendPrefs?.map((pref: FileSharePathPreference) => {
          const key = makeMapKey(pref.type, pref.name);
          return { [key]: pref };
        }) || [];
      const fspMap = Object.assign({}, ...fspArray);
      if (fspMap) {
        updateLocalFspPreferenceStates(fspMap);
      }
    })();
  }, [isZonesMapReady, fetchPreferences, updateLocalFspPreferenceStates]);

  React.useEffect(() => {
    if (!isZonesMapReady) {
      return;
    }

    (async function () {
      const backendPrefs = await fetchPreferences('folder');
      const folderArray =
        backendPrefs?.map((pref: FolderPreference) => {
          const key = makeMapKey(
            pref.type,
            `${pref.fspName}_${pref.folderPath}`
          );
          return { [key]: pref };
        }) || [];
      const folderMap = Object.assign({}, ...folderArray);
      if (folderMap) {
        updateLocalFolderPreferenceStates(folderMap);
      }
    })();
  }, [isZonesMapReady, fetchPreferences, updateLocalFolderPreferenceStates]);

  return (
    <PreferencesContext.Provider
      value={{
        pathPreference,
        showPathPrefAlert,
        setShowPathPrefAlert,
        handlePathPreferenceSubmit,
        zonePreferenceMap,
        zoneFavorites,
        fileSharePathPreferenceMap,
        fileSharePathFavorites,
        folderPreferenceMap,
        folderFavorites,
        isFileSharePathFavoritesReady,
        handleFavoriteChange
      }}
    >
      {children}
    </PreferencesContext.Provider>
  );
};
