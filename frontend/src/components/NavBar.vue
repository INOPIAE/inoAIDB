<template>
  <v-navigation-drawer>
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
            <span class="link-text">{{ item.title }}</span>
          </a>
        </template>
        <template v-else>
          <router-link
            :to="item.href"
            :style="{ paddingLeft: `${item.level ? item.level * 20 : 0}px` }"
            @click="item.onClick ? item.onClick() : null"
          >
            <v-icon :icon="item.icon" />
            <span class="link-text">{{ item.title }}</span>
          </router-link>
        </template>
      </v-list-item>
    </template>
  </v-navigation-drawer>
</template>

<script>
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

export default {
    setup() {
        const authStore = useAuthStore(); // Access the Pinia store

        // Define navigation items
        const items = computed(() => [
            {
                title: 'Home',
                icon: `mdi-home`,
                href: '/home',
                condition: null,
            },
            {
                style: 'divider',
            },
            {
                title: 'Applications',
                icon: `mdi-application-outline`,
                href: '/applications',
                condition: null,
            },
            {
                title: 'Manufacturers',
                icon: `mdi-warehouse`,
                href: '/manufacturers',
                condition: null,
            },
            {
                style: 'divider',
            },
            {
                title: 'Account',
                icon: `mdi-account`,
                href: '/userprofile',
                condition: () => authStore.isAuthenticated,
            },
            {
                title: 'Login',
                icon: `mdi-login`,
                href: '/login',
                condition: () => !authStore.isAuthenticated,
                level: 1,
            },
            {
                title: 'Invite',
                icon: `mdi-account-plus`,
                href: '/invite',
                condition: () => authStore.isAuthenticated,
                level: 1,
            },
            {
                title: 'Logout',
                icon: `mdi-logout`,
                href: "#", // Use href as placeholder (or null)
                onClick: () => authStore.logout(),
                condition: () => authStore.isAuthenticated,
                level: 1,
            },
            {
                title: 'Register',
                icon: `mdi-account-edit`,
                href: '/register',
                condition: () => !authStore.isLoggedIn,
                level: 1,
            },
            {
                style: 'divider',
                condition: () => authStore.isLoggedIn,
            },

            {
                style: 'divider',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
            },
            {
                title: 'Administration',
                icon: `mdi-account`,
                href: '/userprofile',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
            },
            {
                title: 'User administration',
                icon: `mdi-account-supervisor`,
                href: '/adminusers',
                condition: () => authStore.isAuthenticated && authStore.user?.is_admin,
                level: 1,
            },
            {
                style: 'divider',
            },
            {
                title: 'API Documentation',
                style: 'external',
                icon: 'mdi-api',
                href: 'http://localhost:8000/docs',
                condition:  null,
            },
            {
                title: 'About',
                icon: `mdi-information-variant`,
                href: '/about',
                condition:  null,
            },
                        {
                title: 'Imprint',
                icon: `mdi-information-variant`,
                href: '/imprint',
                condition:  null,
            },            {
                title: 'Data Protection',
                icon: `mdi-information-variant`,
                href: '/dataprotection',
                condition:  null,
            },
        ]);

        return {
            authStore,
            items,
        };
    },
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
