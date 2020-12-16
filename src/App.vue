<template>
  <v-app id="inspire">
    <v-navigation-drawer
            v-if="validation.validationAccepted === true"
            v-model="drawer"
            app
            :clipped="$vuetify.breakpoint.lgAndUp"
            color="primary"
    >
      <LeftBar/>
    </v-navigation-drawer>

    <v-app-bar
            app
            dark
            :clipped-left="$vuetify.breakpoint.lgAndUp"
            color="primary darken-3"
    >
      <v-app-bar-nav-icon
              v-show="validation.validationAccepted === true"
              @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>
      <v-toolbar-title>Valexa</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container
              fluid
      >
        <v-row align="start" justify="center">
          <v-col>
            <IPCListener/>
            <router-view/>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-footer
            app
            dark
            color="primary darken-3"
    >
      <span class="white--text">&copy; {{ new Date().getFullYear() }}</span>
    </v-footer>
  </v-app>
</template>

<script>
  import LeftBar from "./components/LeftBar";
  const electron = require('electron')
  const ipcRenderer = electron.ipcRenderer
  const loadBalancer = require('electron-load-balancer')
  import { mapMutations, mapGetters, mapState } from 'vuex'
  import IPCListener from "./components/IPCListener"

  export default {
    components: {
      IPCListener,
      LeftBar
    },
    props: {
      source: String,
    },
    computed: {
      ...mapState([
        'validation'
      ])
    },
    mounted: function () {
      ipcRenderer.on("GEN_MESSAGE", (event, args) => {
        console.log(args)
      })
    },
    data: () => ({
      drawer: null,
      pyMessage: ""
    }),
  }
</script>

<style>
  .no-scroll > * {
    overflow-x: hidden !important;
  }
  .v-navigation-drawer {
    z-index: 999999 !important;
  }

  .v-app-bar {
    z-index: 99999 !important;
  }

  .v-footer {
    z-index: 99999 !important;
  }
</style>