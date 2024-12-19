import useDebounce from "./useDebounce";
import useThrottle from "./useThrottle";
import useCopy from './useCopy'

const myCommand = (Vue) => {
    Vue.directive('debounce', useDebounce.bind)
    Vue.directive('throttle', useThrottle.bind)
    Vue.directive('copy', useCopy)
}

export default myCommand;