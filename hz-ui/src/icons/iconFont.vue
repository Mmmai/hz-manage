<template>
  <svg
    class="iconfont-js"
    :style="{ 'font-size': size+'px' }"
    aria-hidden="true"
  >
    <use :xlink:href="iconClass"></use>
  </svg>
</template>

<script>
export default {
  name: "iconfontSvg",
  props: {
    //图标的名称
    icon: {
      type: String,
      required: true,
    },
    //图标的font-size，单位是px
    size: {
      type: String,
      default: ""
    }
  },
  computed: {
    iconClass() {
      return `#${this.icon}`
    }
  }
};
</script>

<style>
.iconfont-js {
  width: 1em;
  height: 1em;
  vertical-align: -0.15em;
  fill: currentColor;
  overflow: hidden;
}
</style>
