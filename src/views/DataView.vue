<i18n>
    {
        "en": {
            "header": {
                "title": "Data Entry",
                "description": "Please enter the data for each compound"
            },
            "card": {
                "compound" : "Compound",
                "enterCompound": "Add a compound to continue",
                "lblCompound": "Compound",
                "hintCompound": "Enter the name of the compound or target for these data",
                "btnContinue": "Continue",
                "btnEdit": "Edit Name",
                "btnSave": "Save",
                "errNameEmpty": "The name must not be empty",
                "errNameExist": "This compound already exist",
                "btnDelete": "Delete this compound",
                "btnAddCalib": "Add calibration data",
                "btnDeleteCalib": "Delete calibration data",
                "table": {
                    "lblSeries": "Series",
                    "lblLevel": "Level",
                    "lblRep": "Replicate",
                    "lblX": "X",
                    "lblSupp": "Additional Row",
                    "btnAdd": "Add Row",
                    "btnReset": "Reset Data",
                    "btnResize": "Resize Table",
                    "validation": "Validation",
                    "calibration": "Calibration",
                    "data": {
                        "series": "Series",
                        "level": "Level",
                        "x": "X",
                        "y": "Replicate ",
                        "validation": "Validation Data",
                        "calibration": "Calibration Data"
                    }
                }
            }
        },
        "fr": {
            "header": {
                "title": "Entrée de données",
                "description": "Entrer les données pour chacun des composés"
            },
            "card": {
                "compound" : "Composé",
                "enterCompound": "Ajouter un composé pour continuer",
                "lblCompound": "Composé",
                "hintCompound": "Entrer le nom du composé ou de la cible qui correspond à ce données",
                "btnContinue": "Continuer",
                "btnEdit": "Modifier le nom",
                "btnSave": "Enregistrer",
                "errNameEmpty": "Le nom ne doit pas être vide",
                "errNameExist": "Le composé existe déjà",
                "btnDelete": "Effacer ce composé",
                "btnAddCalib": "Ajouter des données de calibration",
                "btnDeleteCalib": "Effacer les données de calibration",
                "table": {
                    "lblSeries": "Série",
                    "lblLevel": "Niveau",
                    "lblRep": "Réplicat",
                    "lblX": "X",
                    "lblSupp": "Rangée Supplémentaire",
                    "btnAdd": "Ajouter une rangé",
                    "btnReset": "Effacer les données",
                    "btnResize": "Redimensionner le tableau",
                    "validation": "Validation",
                    "calibration": "Calibration",
                    "data": {
                        "series": "Série",
                        "level": "Niveau",
                        "x": "X",
                        "y": "Repétition ",
                        "validation": "Données de Validation",
                        "calibration": "Données de Calibration"
                    }
                }
            }
        }
    }
</i18n>

<template>
    <div>
        <DataHeader :language-text="$t('header')"/>
        <v-card class="secondary" shaped elevation="2">
            <v-card-text>
                <v-row>
                    <v-col>
                        <v-card shaped flat>
                            <v-expansion-panels light multiple accordion>
                                <DataCard :language-text="$t('card')" v-for="(key) in getListOfCompound" :load-data-from="key" :key="key" />
                                <DataCard :language-text="$t('card')" :key="blankCardKey"/>
                            </v-expansion-panels>
                        </v-card>
                    </v-col>
                </v-row>

            </v-card-text>
        </v-card>
    </div>
</template>

<script>
    import DataCard from "../components/data/DataCard";
    import DataHeader from "../components/data/DataHeader";
    import { mapGetters, mapState } from "vuex";

    export default {
        name: 'data-view',
        components: {
            DataHeader,
            DataCard,
        },
        computed:{
            ...mapGetters([
                'getNumberOfCompound',
                'getListOfCompound'
            ])
        },
        watch: {
            getNumberOfCompound: function () {
                this.blankCardKey = !this.blankCardKey
            }
        } ,
        data: () => ({
            blankCardKey: 0
        })
    }
</script>

<style scoped>
</style>