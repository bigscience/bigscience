function findIndex(nodes, value, start, stop) {
    // Find the index in the color array for which
    // nodes[index].value <= value < nodes[index + 1]
    if (stop <= start) {
        return start;
    }
    const index = Math.floor(start + (stop - start) / 2);
    const delta = value - nodes[index].value;
    const delta1 = value - nodes[index + 1].value;
    if (delta < 0) {
        return findIndex(nodes, value, start, index - 1);
    }
    else if (delta1 < 0) {
        return index;
    }
    else {
        return findIndex(nodes, value, index + 1, stop);
    }
}
const linearMixer = (value, lowerNodeValue, upperNodeValue) => {
    const frac = (value - lowerNodeValue) / (upperNodeValue - lowerNodeValue);
    return [1 - frac, frac];
};

function isNode(node) {
    return node.value !== undefined && node.mapped !== undefined;
}
function isNodeArray(nodes) {
    return nodes.length > 0 && isNode(nodes[0]);
}
function colorCombination(a, X, b, Y) {
    return [
        a * X[0] + b * Y[0],
        a * X[1] + b * Y[1],
        a * X[2] + b * Y[2]
    ];
}
function ensureMixer(mixer) {
    return mixer ? mixer : linearMixer;
}
function createColorMap(colors, scale, mixer) {
    if (!Array.isArray(colors) || colors.length < 1) {
        return noColorMap;
    }
    if (isNodeArray(colors)) {
        return createMapFromNodes(colors, scale, ensureMixer(mixer), colorCombination);
    }
    else {
        return createMapFromArray(colors, scale, ensureMixer(mixer), colorCombination);
    }
}
function createMapFromNodes(nodes, scale, mixer, linearCombination) {
    const sortedNodes = nodes.sort((a, b) => a.value < b.value ? -1 : 1);
    return function (value) {
        const scaledValue = scale(value);
        const index = findIndex(sortedNodes, scaledValue, 0, sortedNodes.length - 1);
        if (index == 0 && scaledValue < sortedNodes[0].value) {
            return sortedNodes[index].mapped;
        }
        else if (index == sortedNodes.length - 1) {
            return sortedNodes[index].mapped;
        }
        const [coeff0, coeff1] = mixer(scaledValue, sortedNodes[index].value, sortedNodes[index + 1].value);
        return linearCombination(coeff0, sortedNodes[index].mapped, coeff1, sortedNodes[index + 1].mapped);
    };
}
function createMapFromArray(arr, scale, mixer, linearCombination) {
    return function (value) {
        const scaledValue = scale(value);
        const indexFloat = (arr.length - 1) * scaledValue;
        if (indexFloat <= 0) {
            return arr[0];
        }
        else if (indexFloat >= arr.length - 1) {
            return arr[arr.length - 1];
        }
        const index = Math.floor(indexFloat);
        const [coeff0, coeff1] = mixer(indexFloat, index, index + 1);
        return linearCombination(coeff0, arr[index], coeff1, arr[index + 1]);
    };
}
function noColorMap(_value) {
    return [0, 0, 0];
}

function linearScale(domain, range) {
    let [d0, d1] = domain;
    const [r0, r1] = range;
    if (Math.abs(d0 - d1) < Number.EPSILON) {
        d1 = d0 + 1;
    }
    return function (value) {
        return r0 + (r1 - r0) * ((value - d0) / (d1 - d0));
    };
}

export { createColorMap, linearScale };
