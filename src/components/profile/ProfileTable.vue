<template>
    <v-card shaped light>
        <v-card-title>Profiles</v-card-title>
        <v-card-text>
            <v-data-table
                v-model="selectedProfiles"
                :single-select="false"
                show-select
                :headers="headers"
                :items="getProfilesTable({compoundName: compoundName})"
                :expanded.sync="expanded"
                dense
                show-expand
                :loading="stateLoading.profile"
            >
                <template v-slot:expanded-item="{ headers, item }">
                    <td :colspan="headers.length">
                        <AccuracyProfile
                              :profile-id="item.id"
                              :compound-name="compoundName"
                              x-axe-string="Level"
                              y-axe-string="Recovery"
                        ></AccuracyProfile>
                    </td>
                </template>
            </v-data-table>
        </v-card-text>

      <v-btn text @click="addReport()" v-bind:disabled="bDisable">Ajouter au rapport</v-btn>

    </v-card>
</template>

<script>
    import { mapMutations, mapGetters, mapState } from 'vuex'
    const electron = require('electron')
    const ipcRenderer = electron.ipcRenderer
    const loadBalancer = require('electron-load-balancer')
    import AccuracyProfile from "./AccuracyProfile";

    export default {
        name: "MainPage",
        components: { AccuracyProfile },
        methods: {
            ...mapMutations(['setProfilesReport']),
          addReport: function() {
            this.bDisable = true
            this.setProfilesReport({profilesReport: this.selectedProfiles})
          }

        },
        computed: {
          ...mapState(['stateLoading']),
          ...mapGetters(['getProfilesTable']),

        },
        props: {
            compoundName: String
        },
        data () {
            return {
              selectedProfiles: [],  //contient les objets selectionnés
              bDisable: false,
              finishedLoading: false,
              expanded: [],
              headers: [
                { text: 'Id', value: 'id' },
                { text: 'Model', value: 'model_info.model_name' },
                { text: 'LOD', value: 'model_info.lod' },
                { text: 'Min LOQ', value: 'model_info.min_loq' },
                { text: 'Max LOQ', value: 'model_info.max_loq' },
                { text: '', value: 'data-table-expand' },
              ]
            }
        }
    }
</script>

<style scoped>

</style>