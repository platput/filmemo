<template>
    <v-card class="py-5 mb-5 mx-5" variant="flat" rounded="false">
        <v-card-title>Share Game URL: </v-card-title>
        <v-card-item>
            <v-text-field :readonly=true density="compact" variant="outlined" append-inner-icon="fa-solid fa-paste" @click="copyCurrentUrlToClipboard">
                {{ gameSore.getGameId() }}
            </v-text-field>
        </v-card-item>
    </v-card>
</template>

<script setup lang="ts">
import { useGameStore } from '@/stores/game';
const gameSore = useGameStore()
function copyCurrentUrlToClipboard() {
    navigator.clipboard.writeText(window.location.href)
}
</script>