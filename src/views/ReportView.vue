<i18n>
{
	"en": {
		"header": {
			"title": "Validation Report",
			"description": ""
		},
		"titleInfo": "Report Information",
		"titleGeneration": "Generate",
		"optionGeneration": {
			"graph": "Graphs (PNG format)",
			"tex": "TEX project"
		},
		"labelBtn": "Generate the report",
		"alert": {
			"infoEmpty": "Please select profiles from the left Profiles tab",
			"optionEmpty":"Please select generation options behind",
			"infoTex": "Template differ from PDF and Word files"
		}
	},
	"fr": {
		"header": {
			"title": "Rapport de Validation",
			"description": ""
		},
		"titleInfo": "Informations contenues dans le rapport",
		"titleGeneration": "Génération",
		"optionGeneration": {
			"graph": "Graphiques (format PNG)",
			"tex": "Projet TEX"
		},
		"labelBtn": "Génération du rapport",
		"alert": {
			"infoEmpty": "Veuillez selectionner des profiles dans l'onglet de gauche Profiles",
			"optionEmpty":"Veuillez selectionner vos options de génération de rapport ci-dessous",
			"infoTex": "Template différent du word et pdf"
		}
	}
}
</i18n>


<template>
  <v-card class="secondary" shaped elevation="2">
    <v-card-title>{{ $t('header.title') }}</v-card-title>
    <v-card-text>
      <v-row>
        <v-col>
          <v-card shaped flat>
            <v-card-title>{{ $t('titleInfo') }}</v-card-title>
            <v-card-text>
              <v-list-item v-if="this.profilesReport.length === 0">
                <v-list-item-content>
                  <v-list-item-title>
                    <v-alert dense outlined type="warning">{{ $t('alert.infoEmpty') }}</v-alert>
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              <v-list-item two-line v-for="comp in this.profilesReport">
                <v-list-item-content>
                  <v-list-item-title>{{comp.compound_name}}</v-list-item-title>
                  <v-list-item-subtitle>{{comp.model_info.model_name}}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-card shaped flat>
            <v-card-title>{{ $t('titleGeneration') }}</v-card-title>
            <v-card-text>
              <v-alert dense outlined type="warning" v-if="this.typeReport.length === 0">{{ $t('alert.optionEmpty') }}</v-alert>
              <v-row>
                <v-col>
                  <v-card shaped light>
                    <v-col>
                      <v-checkbox v-model="typeReport" label="Word" value="word"></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox v-model="typeReport" label="PDF" value="pdf"/>
                    </v-col>
                  </v-card>
                </v-col>
                <v-col>
                  <v-card shaped light>
                    <v-col>
                      <v-alert dense outlined type="info">{{ $t('alert.infoTex') }}</v-alert>
                      <v-checkbox v-model="typeReport" v-bind:label="$t('optionGeneration.tex')" value="tex"/>
                    </v-col>
                  </v-card>
                </v-col>
              </v-row>
              <v-row>
                <v-col>
                  <v-card shaped light>
                    <v-col>
                      <v-checkbox v-model="typeReport" v-bind:label="$t('optionGeneration.graph')" value="graph"/>
                    </v-col>
                  </v-card>
                </v-col>
              </v-row>
              <v-row>
                <v-btn color="primary" rounded block @click="createReport()" v-bind:disabled="this.beDisable">{{ $t('labelBtn') }}</v-btn>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>


<script>
import { mapState } from 'vuex'
const electron = require('electron')
const ipcRenderer = electron.ipcRenderer
const loadBalancer = require('electron-load-balancer')

export default {
  name: "ReportView",
  data: () => ({
    typeReport: ["pdf", "word"]
  }),
  mounted() {
    ipcRenderer.on("CHANNEL_PROFILES_REPORT", (event, args) => {  // LISTENER CHANNEL
      console.log("Listener sur CHANNEL_PROFILES_REPORT: "+ JSON.stringify(args).toString())
      if(JSON.stringify(args).toString() === '"processProfilesReport READY"'){  // le process peut recueillir des infos
        loadBalancer.sendData(ipcRenderer, 'processProfilesReport', {data: {profiles: this.profilesReport, typeReport: this.typeReport}})  //TODO: + tex pdf
      }
      if(args.type === "END"){
        loadBalancer.sendData(ipcRenderer, 'processProfilesReport', {data: 'EXIT'})  //stop process
      }
    })
  },
  computed: {
    ...mapState(['profilesReport']),
    beDisable: function(){
      return !(this.profilesReport.length > 0 && this.typeReport.length > 0);
    }
  },
  methods: {
    createReport: function(){
      loadBalancer.start(ipcRenderer, 'processProfilesReport')
    }
  }
}
</script>

<style scoped>

</style>