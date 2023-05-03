<template>
    <v-sheet class="pt-5">
        <p class="text-h1 text-center">
            {{ props.emoji }}
        </p>
        <v-row>
            <v-col class="text-center">
                <v-text-field v-model="movieName" variant="solo" class="ma-5"></v-text-field>
                <v-btn type="compact" variant="flat" rounded="false" @click="submit" class="mx-5" :loading="isLoading">Submit Guess</v-btn>
            </v-col>
        </v-row>
        
    </v-sheet>
</template>

<script setup lang="ts">import { ref } from 'vue';
const emit = defineEmits(['submitGuess'])
const props = defineProps({
    emoji: String
})
const movieName = ref("")
const isLoading = ref(false)
function submit() {
    isLoading.value = true
    emit('submitGuess', movieName.value)
}
</script>