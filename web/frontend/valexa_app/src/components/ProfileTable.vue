<template>
<table>
	<tbody>
		<tr>
			<th>File name</th>
			<th colspan="7" style="text-align: center;">{{filename}}</th>
		</tr>
		<tr>
			<td>Modèle</td>
			<td colspan="3">{{profile.model.name}}</td>
			<td>beta</td>
			<td>{{ profile.tolerance_limit }}</td>
			<td>t</td>
			<td>{{ profile.acceptance_limit }}</td>
		</tr>
		<tr>
			<td>LOQ Min</td>
			<td colspan="3">{{ profile.min_lq }}</td>
			<td>LOQ Max</td>
			<td colspan="3">{{ profile.max_lq }}</td>
		</tr>
		<tr>
			<td>LOD</td>
			<td colspan="3">{{ profile.ld }}</td>
			<td>Corr. Factor.</td>
			<td>{{ profile.model.correction_factor }}</td>
			<td>Recovery</td>
			<td>{{(1 / profile.model.correction_factor) * 100}}</td>
		</tr>
		<tr>
			<td colspan="8"></td>
		</tr>
		<tr>
			<td rowspan="2">Concentration</td>
			<td rowspan="2">Mesuré</td>
			<td colspan="2">Exactitude</td>
			<td colspan="2">Précision</td>
			<td colspan="2">Justesse</td>
		</tr>
		<tr>
			<td>Biais absolue</td>
			<td>Biais relatif</td>
			<td>Répétabilité (% RSD)</td>
			<td>Intermédiaire (% RSD)</td>
			<td>Limite de tolérance</td>
			<td>Limite relative</td>
		</tr>
		<tr v-for="(level, i) in profile.levels" v-bind:key="i"> 
			<td>{{roundUp(level["introduced_concentration"], 3)}}</td>
			<td>{{roundUp(level["calculated_concentration"], 3)}}</td>
			<td>{{roundUp(level["bias"], 3)}}</td>
			<td>{{roundUp(level["relative_bias"], 2)}}</td>
			<td>{{roundUp(level["repeatability_var"], 3)}}</td>
			<td>{{roundUp(level["repeatability_std"], 3)}}</td>
			<td>{{roundUp(level["abs_tolerance"], 2)}}</td>
			<td>{{roundUp(level["rel_tolerance"], 2)}}</td>
		</tr>
		<tr>
			<td colspan="8"></td>
		</tr>
	</tbody>
</table>
</template>

<script>
import {fixedDecimals} from "../js/math_utils"

export default {
	name: "ProfileTable",
	//TODO stricter type control 
  props: {
		filename: String,
    profile: Object,
  },
  data() {
    return {};
	},
	methods: {
		roundUp(value, decimals) { 
			if (typeof value === "object") {
				var newVal = [];
				for (const val of value) {
					newVal.push(+fixedDecimals(val, decimals));
				}
				return newVal;
			} else {
				return fixedDecimals(value, decimals); 
			}
		},
	}
};
</script>

<style scoped>
table {
  border: 2px solid #000000;
  text-align: left;
  border-collapse: collapse;
	margin-left: auto;
  margin-right: auto;
}
table td, th {
  border: 1px solid #000000;
  padding: 5px 4px;
}
table tbody td {
  font-size: 13px;
}
table thead {
  background: #CFCFCF;
  background: -moz-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
  background: -webkit-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
  background: linear-gradient(to bottom, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
  border-bottom: 3px solid #000000;
}
table thead th {
  font-size: 15px;
  font-weight: bold;
  color: #000000;
  text-align: left;
}
table tfoot {
  font-size: 14px;
  font-weight: bold;
  color: #000000;
  border-top: 3px solid #000000;
}
table tfoot td {
  font-size: 14px;
}
</style>


