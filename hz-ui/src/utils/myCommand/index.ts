import useDebounce from "./useDebounce";
import useThrottle from "./useThrottle";
import useCopy from './useCopy'
import userPermission from './permission'
const myCommand = (Vue) => {
    Vue.directive('debounce', useDebounce.bind)
    Vue.directive('throttle', useThrottle.bind)
    Vue.directive('copy', useCopy)
    Vue.directive('permission', userPermission)
}

export default myCommand;