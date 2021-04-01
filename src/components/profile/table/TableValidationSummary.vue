<template>
      <v-row>
        <v-col>
          <v-row>
            <v-col>
              <span class="text-h5">Summary</span>
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
                    <td>LOD</td>
                    <td>{{tableData.lod}} {{tableData.units}} ({{tableData.lod_type}})</td>
                  </tr>
                  <tr>
                    <td>LOQ Min</td>
                    <td>{{tableData.min_loq}} {{tableData.units}}</td>
                  </tr>
                  <tr>
                    <td>LOQ Max</td>
                    <td>{{tableData.max_loq}} {{tableData.units}}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-col>
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
                    <td>Correction</td>
                    <td>
                      <span v-if="tableData.has_correction">
                        {{tableData.correction_factor}} ({{tableData.has_correction}})

                        <span v-if="tableData.forced_correction_value>0">(Forced)</span>
                      </span>
                      <span v-else>---</span>
                    </td>
                  </tr>
                  <tr>
                    <td>Average Recovery</td>
                    <td>{{tableData.average_recovery}}</td>
                  </tr>
                  <tr>
                    <td>Tolerance</td>
                    <td>{{tableData.tolerance}} %</td>
                  </tr>
                  <tr>
                    <td>Acceptance</td>
                    <td>
                      {{tableData.acceptance}}
                      <span v-if="tableData.absolute_acceptance"> {{tableData.units}} (Absolute)</span>
                      <span v-else> % (Relative)</span>
                    </td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
</template>

<script>
  export default {
    name: "TableValidationSummary",
    props: {
      tableData: Object
    }
  }
</script>

<style scoped>

</style>