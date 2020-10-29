<template>
    <v-list
            dense
            shaped
    >
        <v-list-item-group>
            <v-list-item
                    v-for="(item, i) in items"
                    :key="i"
                    :to="item.to"
            >
                <v-list-item-action>
                    <v-icon v-text="item.icon"></v-icon>
                </v-list-item-action>
                <v-list-item-content>
                    <v-list-item-title v-text="item.text"/>
                </v-list-item-content>
                <v-list-item-icon v-if="item.to==='data'">
                    <CompoundsBadge :text-item="item.text"/>
                </v-list-item-icon>
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
    import { mapGetters } from 'vuex'
    import CompoundsBadge from "./CompoundsBadge";

    export default {
        name: "LeftBar",
        components: {CompoundsBadge},
        data () {
            return {
                items: {
                    main: {
                        icon: 'mdi-home',
                        text: 'Home',
                        to: '/'
                    },
                    data: {
                        icon: 'mdi-table',
                        text: 'Data',
                        to: 'data'
                    },
                    settings: {
                        icon: 'mdi-tune',
                        text: 'Settings',
                        to: 'settings'
                    },
                    profile: {
                        icon: 'mdi-chart-line',
                        text: 'Profiles',
                        to: 'profiles'
                    },
                    report: {
                        icon: 'mdi-file-chart-outline',
                        text: 'Report',
                        to: 'report'
                    },
                }
            }
    }
    }
</script>

<style scoped>

</style>