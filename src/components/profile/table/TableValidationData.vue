<template>
  <v-row>
    <v-col>
      <span class="text-h5">Validation Data</span>
      <v-data-table
        dense
        :headers="headers"
        :items="tableData"
        class="elevation-1"
        hide-default-footer
        :items-per-page=1000
      >
      </v-data-table>
    </v-col>
  </v-row>
</template>

<script>
  export default {
    name: "TableValidationData",
    props: {
      tableData: Array
    },
    computed: {
      headers: function () {
        var header = [
          {text: 'Series', value: 'Series'},
          {text: 'Level', value: 'Level'},
          {text: 'X', value: 'x'},
          {text: 'Y', value: 'y'},
        ]
        if (this.tableData[0].hasOwnProperty('x_raw')) {
          header.push(
              {text: 'Corrected Y', value: 'y_corr'},
              {text: 'Calculated', value: 'x_raw'},
              {text: 'Corrected', value: 'x_calc'}
              )
        } else {
          header.push({text: 'Calculated', value: 'x_calc'})
        }
        header.push(
          {text: 'Abs. Bias', value: 'bias_abs'},
          {text: 'Rel. Bias', value: 'bias_rel'}
        )
        return header
      },
    }
  }
</script>

<style scoped>

</style>