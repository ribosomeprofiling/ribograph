<script setup lang="ts">

</script>

<template>
    <span class="skeleton-box"></span>
</template>


<style scoped>
.skeleton-box {
	display: inline-block;
	height: 1em;
	position: relative;
	overflow: hidden;
	background-color: #DDDBDD;
  width: 100%;
  border-radius: 8px;
}

.skeleton-box::after {
	position: absolute;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	transform: translateX(-100%);
	background-image: linear-gradient(90deg, rgba(255, 255, 255, 0) 0, rgba(255, 255, 255, 0.2) 20%, rgba(255, 255, 255, 0.5) 60%, rgba(255, 255, 255, 0));
	animation: shimmer 2s infinite;
	content: '';
}

@keyframes shimmer {
	100% {
		transform: translateX(100%);
	}
}
</style>