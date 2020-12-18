<template>
      <v-row>
        <v-col>
          <span class="text-h5">Uncertainty</span>
          <v-data-table
            dense
            :headers="headers"
            :items="items"
            class="elevation-1"
            hide-default-footer
            :items-per-page=1000
          />
        </v-col>
      </v-row>
</template>

<script>
  export default {
    name: "TableValidationUncertainty",
    props: {
      tableData: Object
    },
    computed: {
      items: function() {
        var itemsArray = []
        this.tableData.levels_info.forEach((value, index) => {
          itemsArray[index] = {index: index, ...value}
        })
        this.tableData.uncertainty_info.forEach((value, index) => {
          itemsArray[index] = {...itemsArray[index], ...value}
        })
        return itemsArray
      }
    },
    data: () => ({
      headers: [
        {
          text: 'Level',
          value: 'index'
        },
        {
          text: 'Introduced Concentration',
          value: 'introduced_concentration'
        },
        {
          text: 'Calculated Concentration',
          value: 'calculated_concentration'
        },
        {
          text: 'Absolute Expanded Uncertainty',
          value: 'uncertainty_abs'
        },
        {
          text: 'PC Expanded Uncertainty',
          value: 'uncertainty_pc'
        }
      ]
    })
  }
</script>

<style scoped>

</style>