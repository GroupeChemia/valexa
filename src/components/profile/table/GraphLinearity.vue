<template>
  <v-row>
    <v-col>
      <v-row>
        <v-col>
          <span class="text-h5">Linearity</span>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-row>
            <v-col>
              <VuePlotly
                  :data="graphsData.linearity.data"
                  :layout="graphsData.linearity.layout"
                  :display-mode-bar="false"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-simple-table
                  dense
                  class="elevation-1"
              >
                <thead>
                <tr>
                  <th class="text-left">Parameter</th>
                  <th class="text-left">Value</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td>Slope</td>
                  <td>{{tableData.linearity_info.slope.value}}</td>
                </tr>
                <tr>
                  <td>Intercept</td>
                  <td>{{tableData.linearity_info.intercept.value}}</td>
                </tr>
                <tr>
                  <td>R²</td>
                  <td>{{tableData.linearity_info.rsquared.value}}</td>
                </tr>
                </tbody>
              </v-simple-table>
            </v-col>
          </v-row>
        </v-col>
        <v-col v-if="hasCorrection">
          <v-row>
            <v-col>
              <VuePlotly
                  :data="graphsData.correction.data"
                  :layout="graphsData.correction.layout"
                  :display-mode-bar="false"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-simple-table
                  dense
                  class="elevation-1"
              >
                <thead>
                <tr>
                  <th class="text-left">Parameter</th>
                  <th class="text-left">Value</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td>Slope</td>
                  <td>{{tableData.correction_info.slope.value}}</td>
                </tr>
                <tr>
                  <td>Intercept</td>
                  <td>{{tableData.correction_info.intercept.value}}</td>
                </tr>
                <tr>
                  <td>R²</td>
                  <td>{{tableData.correction_info.rsquared.value}}</td>
                </tr>
                </tbody>
              </v-simple-table>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>
  import VuePlotly from '@statnett/vue-plotly'

  export default {
    name: "GraphLinearity",
    props: {
      hasCorrection: String,
      graphsData: Object,
      tableData: Object
    },
    components: {
      VuePlotly
    }
  }
</script>

<style scoped>

</style>