<template>
    <v-card class="py-5 mb-5 mx-5" variant="flat" rounded="false">
        <v-card-title>Share Game URL: </v-card-title>
        <v-card-item>
            <v-row>
                <v-col cols="9">
                    <v-text-field density="compact" readonly :value="getShareUrl()" outlined></v-text-field>
                </v-col>
                <v-col cols="3">
                    <v-btn color="primary" @click="copyCurrentUrlToClipboard()">
                        <v-icon icon="fa-regular fa-paste"></v-icon>
                    </v-btn>
                </v-col>
            </v-row>
        </v-card-item>
    </v-card>
</template>

<script setup lang="ts">
// import { useGameStore } from '@/stores/game';
// const gameStore = useGameStore()
function copyCurrentUrlToClipboard() {
    navigator.clipboard.writeText(getShareUrl())
}
function getShareUrl() {
    return window.location.href + "/join"
}
</script>