<template>
  <v-navigation-drawer
    v-model="drawerModel"
    app
    :temporary="isMobile"
    :permanent="!isMobile"
  >
    <v-list density="compact">
      <template v-for="(item, index) in items" :key="index">
        <v-list-item v-if="!item.condition || item.condition()">
          <template v-if="item.style === 'divider'">
            <v-divider />
          </template>
          <template v-else-if="item.style === 'external'">
            <a
              :href="item.href"
              :style="{ paddingLeft: `${item.level ? item.level * 20 : 0}px` }"
              target="_blank"
              rel="noopener noreferrer"
              @click="item.onClick ? item.onClick() : null"
            >
              <v-icon :icon="item.icon" />
              <span class="link-text">{{ t(item.title) }}</span>
            </a>
          </template>
          <template v-else>
            <router-link
              :to="item.href"
              :style="{ paddingLeft: `${item.level ? item.level * 20 : 0}px` }"
              @click="() => handleItemClick(item)"
            >
              <v-icon :icon="item.icon" />
              <span class="link-text">{{ t(item.title) }}</span>
            </router-link>
          </template>
        </v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useI18n } from "vue-i18n";
import { useDisplay } from "vuetify";

export default {
  props: {
    drawer: Boolean
  },
  emits: ['update:drawer'],
  setup(props, { emit }) {
    const { mobile } = useDisplay();
    const isMobile = computed(() => mobile.value);

    const updateDrawer = (val) => emit('update:drawer', val);

    const drawerModel = computed({
      get: () => props.drawer,
      set: (val) => updateDrawer(val)
    });

    const authStore = useAuthStore();
    const { t } = useI18n();

    const backendUrl = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";
    const raw_mount = import.meta.env.VITE_ROOT_MOUNT;
    const root_mount = (!raw_mount || raw_mount.toLowerCase() === "none") ? "" : raw_mount;

    const handleItemClick = (item) => {
      if (item.onClick) item.onClick();
      if (isMobile.value) updateDrawer(false);
    };

        const items = computed(() => [
            {
                title: 'home',
                icon: `mdi-home`,
                href: '/home',
                condition: null,
            },
            {
                style: 'divider',
            },
            {
                title: 'applications',
                icon: `mdi-application-outline`,
                href: '/applications',
                condition: null,
            },
            {
                style: 'divider',
            },
            {
                title: 'account',
                icon: `mdi-account`,
                href: '/userprofile',
                condition: () => authStore.isAuthenticated,
            },
            {
                title: 'login',
                icon: `mdi-login`,
                href: '/login',
                condition: () => !authStore.isAuthenticated,
                level: 1,
            },
            {
                title: 'logout',
                icon: `mdi-logout`,
                href: "#", // Use href as placeholder (or null)
                onClick: () => authStore.logout(),
                condition: () => authStore.isAuthenticated,
                level: 1,
            },
            {
                title: 'register',
                icon: `mdi-account-edit`,
                href: '/register',
                condition: () => !authStore.isAuthenticated,
                level: 1,
            },
            {
                style: 'divider',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
            },
            {
                title: 'administration',
                icon: `mdi-account`,
                href: '/userprofile',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
            },
                        {
                title: 'invite',
                icon: `mdi-account-plus`,
                href: '/invite',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                title: 'userAdministration',
                icon: `mdi-account-supervisor`,
                href: '/adminusers',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                title: 'payments',
                icon: `mdi-account-supervisor`,
                href: '/payments',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                title: 'manufacturer',
                icon: `mdi-warehouse`,
                href: '/manufacturers',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                title: 'languageModels',
                icon: `mdi-account-supervisor`,
                href: '/languagemodel',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                style: 'divider',
            },
            {
                title: 'apiDocumentation',
                style: 'external',
                icon: 'mdi-api',
                href: `${backendUrl}${root_mount}/docs`,
                condition:  null,
            },
            {
                title: 'about',
                icon: `mdi-information-variant`,
                href: '/general/about',
                condition:  null,
            },
                        {
                title: 'imprint',
                icon: `mdi-information-variant`,
                href: '/general/imprint',
                condition:  null,
            },            {
                title: 'dataprotection',
                icon: `mdi-information-variant`,
                href: '/general/dataprotection',
                condition:  null,
            },
        ]);


    return {
      drawerModel,
      isMobile,
      items,
      handleItemClick,
      t
    };
  }
};
</script>

<style scoped>
a {
  text-decoration: none;
  font-weight: normal;
}

a .link-text {
  padding-left: 4px;
}

a:hover .link-text, a:active .link-text {
  text-decoration: underline;
}

.router-link-active {
  font-weight: bold;
}
</style>
