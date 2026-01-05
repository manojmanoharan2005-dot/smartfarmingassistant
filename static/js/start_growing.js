// Task Management System
const cropName = document.body.dataset.cropName;
const storageKey = `tasks_${cropName}`;

// Define crop-specific tasks for each of the 24 crops
const cropSpecificTasks = {
    // GRAINS & CEREALS
    'rice': [
        { value: 'Field Preparation & Leveling', icon: '🚜', label: 'Field Preparation & Leveling' },
        { value: 'Nursery Bed Preparation', icon: '🌱', label: 'Nursery Bed Preparation' },
        { value: 'Seedling Transplanting', icon: '🌾', label: 'Seedling Transplanting' },
        { value: 'Water Management', icon: '💧', label: 'Water Management' },
        { value: 'Fertilizer Application', icon: '🧪', label: 'Fertilizer Application' },
        { value: 'Weeding & Intercultivation', icon: '🌿', label: 'Weeding & Intercultivation' },
        { value: 'Pest & Disease Control', icon: '🐛', label: 'Pest & Disease Control' },
        { value: 'Panicle Initiation Check', icon: '🌾', label: 'Panicle Initiation Check' },
        { value: 'Harvesting', icon: '⚙️', label: 'Harvesting' },
        { value: 'Threshing & Winnowing', icon: '🏪', label: 'Threshing & Winnowing' }
    ],
    'wheat': [
        { value: 'Land Plowing & Harrowing', icon: '🚜', label: 'Land Plowing & Harrowing' },
        { value: 'Seed Treatment', icon: '🌱', label: 'Seed Treatment' },
        { value: 'Sowing (Line/Broadcasting)', icon: '🌾', label: 'Sowing (Line/Broadcasting)' },
        { value: 'First Irrigation (CRI Stage)', icon: '💧', label: 'First Irrigation (CRI Stage)' },
        { value: 'Top Dressing Fertilizer', icon: '🧪', label: 'Top Dressing Fertilizer' },
        { value: 'Weed Control', icon: '🌿', label: 'Weed Control' },
        { value: 'Rust & Aphid Management', icon: '🐛', label: 'Rust & Aphid Management' },
        { value: 'Ear Formation Monitoring', icon: '🌾', label: 'Ear Formation Monitoring' },
        { value: 'Harvesting at Maturity', icon: '⚙️', label: 'Harvesting at Maturity' },
        { value: 'Grain Storage', icon: '🏪', label: 'Grain Storage' }
    ],
    'maize': [
        { value: 'Soil Preparation', icon: '🚜', label: 'Soil Preparation' },
        { value: 'Seed Sowing', icon: '🌱', label: 'Seed Sowing' },
        { value: 'Thinning & Gap Filling', icon: '🌾', label: 'Thinning & Gap Filling' },
        { value: 'Irrigation Schedule', icon: '💧', label: 'Irrigation Schedule' },
        { value: 'Nitrogen Application', icon: '🧪', label: 'Nitrogen Application' },
        { value: 'Earthing Up', icon: '🌿', label: 'Earthing Up' },
        { value: 'Stem Borer Control', icon: '🐛', label: 'Stem Borer Control' },
        { value: 'Tasseling & Silking Check', icon: '🌾', label: 'Tasseling & Silking Check' },
        { value: 'Cob Harvesting', icon: '⚙️', label: 'Cob Harvesting' },
        { value: 'Drying & Shelling', icon: '🏪', label: 'Drying & Shelling' }
    ],

    // PULSES & VEGETABLES
    'chickpea': [
        { value: 'Deep Plowing', icon: '🚜', label: 'Deep Plowing' },
        { value: 'Rhizobium Seed Treatment', icon: '🌱', label: 'Rhizobium Seed Treatment' },
        { value: 'Line Sowing', icon: '🫘', label: 'Line Sowing' },
        { value: 'Pre-emergence Herbicide', icon: '🌿', label: 'Pre-emergence Herbicide' },
        { value: 'Irrigation at Branching', icon: '💧', label: 'Irrigation at Branching' },
        { value: 'Phosphorus Application', icon: '🧪', label: 'Phosphorus Application' },
        { value: 'Wilt Disease Monitoring', icon: '🦠', label: 'Wilt Disease Monitoring' },
        { value: 'Pod Borer Spray', icon: '🐛', label: 'Pod Borer Spray' },
        { value: 'Pod Maturity Check', icon: '🫘', label: 'Pod Maturity Check' },
        { value: 'Harvesting & Threshing', icon: '📦', label: 'Harvesting & Threshing' }
    ],
    'lentil': [
        { value: 'Seedbed Preparation', icon: '🚜', label: 'Seedbed Preparation' },
        { value: 'Seed Inoculation', icon: '🌱', label: 'Seed Inoculation' },
        { value: 'Broadcasting/Line Sowing', icon: '🫘', label: 'Broadcasting/Line Sowing' },
        { value: 'Weed Management', icon: '🌿', label: 'Weed Management' },
        { value: 'Light Irrigation', icon: '💧', label: 'Light Irrigation' },
        { value: 'Foliar Spray', icon: '🧪', label: 'Foliar Spray' },
        { value: 'Rust Disease Control', icon: '🦠', label: 'Rust Disease Control' },
        { value: 'Aphid Management', icon: '🐛', label: 'Aphid Management' },
        { value: 'Pod Filling Check', icon: '🫘', label: 'Pod Filling Check' },
        { value: 'Harvesting When Brown', icon: '📦', label: 'Harvesting When Brown' }
    ],
    'pigeonpeas': [
        { value: 'Land Preparation', icon: '🚜', label: 'Land Preparation' },
        { value: 'Seed Treatment with Rhizobium', icon: '🌱', label: 'Seed Treatment with Rhizobium' },
        { value: 'Wide Spacing Sowing', icon: '🫘', label: 'Wide Spacing Sowing' },
        { value: 'First Weeding', icon: '🌿', label: 'First Weeding' },
        { value: 'Minimal Irrigation', icon: '💧', label: 'Minimal Irrigation' },
        { value: 'Basal Fertilizer', icon: '🧪', label: 'Basal Fertilizer' },
        { value: 'Pod Fly Monitoring', icon: '🐛', label: 'Pod Fly Monitoring' },
        { value: 'Staking (if needed)', icon: '🪵', label: 'Staking (if needed)' },
        { value: 'Multiple Pod Pickings', icon: '🫘', label: 'Multiple Pod Pickings' },
        { value: 'Drying & Storage', icon: '📦', label: 'Drying & Storage' }
    ],
    'kidneybeans': [
        { value: 'Fine Seedbed Preparation', icon: '🚜', label: 'Fine Seedbed Preparation' },
        { value: 'Direct Seeding', icon: '🌱', label: 'Direct Seeding' },
        { value: 'Thinning Plants', icon: '🫘', label: 'Thinning Plants' },
        { value: 'Regular Irrigation', icon: '💧', label: 'Regular Irrigation' },
        { value: 'NPK Application', icon: '🧪', label: 'NPK Application' },
        { value: 'Weeding & Earthing', icon: '🌿', label: 'Weeding & Earthing' },
        { value: 'Anthracnose Control', icon: '🦠', label: 'Anthracnose Control' },
        { value: 'Support for Climbing Varieties', icon: '🪵', label: 'Support for Climbing Varieties' },
        { value: 'Pod Harvesting', icon: '🫘', label: 'Pod Harvesting' },
        { value: 'Bean Drying', icon: '📦', label: 'Bean Drying' }
    ],
    'mungbean': [
        { value: 'Soil Preparation', icon: '🚜', label: 'Soil Preparation' },
        { value: 'Seed Sowing', icon: '🌱', label: 'Seed Sowing' },
        { value: 'Gap Filling', icon: '🫘', label: 'Gap Filling' },
        { value: 'First Irrigation', icon: '💧', label: 'First Irrigation' },
        { value: 'Phosphorus Fertilizer', icon: '🧪', label: 'Phosphorus Fertilizer' },
        { value: 'Weeding & Thinning', icon: '🌿', label: 'Weeding & Thinning' },
        { value: 'Yellow Mosaic Virus Check', icon: '🦠', label: 'Yellow Mosaic Virus Check' },
        { value: 'Pod Borer Spray', icon: '🐛', label: 'Pod Borer Spray' },
        { value: 'First Pod Picking', icon: '🫘', label: 'First Pod Picking' },
        { value: 'Second Picking', icon: '📦', label: 'Second Picking' }
    ],
    'mothbeans': [
        { value: 'Land Preparation', icon: '🚜', label: 'Land Preparation' },
        { value: 'Broadcasting Seeds', icon: '🌱', label: 'Broadcasting Seeds' },
        { value: 'Light Irrigation', icon: '💧', label: 'Light Irrigation' },
        { value: 'Minimal Fertilizer', icon: '🧪', label: 'Minimal Fertilizer' },
        { value: 'Weeding (if needed)', icon: '🌿', label: 'Weeding (if needed)' },
        { value: 'Pest Monitoring', icon: '🐛', label: 'Pest Monitoring' },
        { value: 'Drought Tolerance Check', icon: '☀️', label: 'Drought Tolerance Check' },
        { value: 'Pod Development Check', icon: '🫘', label: 'Pod Development Check' },
        { value: 'Harvesting Mature Pods', icon: '📦', label: 'Harvesting Mature Pods' },
        { value: 'Sun Drying', icon: '☀️', label: 'Sun Drying' }
    ],
    'blackgram': [
        { value: 'Seedbed Preparation', icon: '🚜', label: 'Seedbed Preparation' },
        { value: 'Seed Treatment', icon: '🌱', label: 'Seed Treatment' },
        { value: 'Line Sowing', icon: '🫘', label: 'Line Sowing' },
        { value: 'Pre-sowing Irrigation', icon: '💧', label: 'Pre-sowing Irrigation' },
        { value: 'Basal Fertilizer', icon: '🧪', label: 'Basal Fertilizer' },
        { value: 'Intercultivation', icon: '🌿', label: 'Intercultivation' },
        { value: 'Yellow Mosaic Control', icon: '🦠', label: 'Yellow Mosaic Control' },
        { value: 'Pod Borer Management', icon: '🐛', label: 'Pod Borer Management' },
        { value: 'Pod Maturity Check', icon: '🫘', label: 'Pod Maturity Check' },
        { value: 'Harvesting & Threshing', icon: '📦', label: 'Harvesting & Threshing' }
    ],

    // FRUITS
    'apple': [
        { value: 'Pit Digging & Filling', icon: '⛏️', label: 'Pit Digging & Filling' },
        { value: 'Grafted Sapling Planting', icon: '🌱', label: 'Grafted Sapling Planting' },
        { value: 'Drip Irrigation Setup', icon: '💧', label: 'Drip Irrigation Setup' },
        { value: 'Organic Manure Application', icon: '🧪', label: 'Organic Manure Application' },
        { value: 'Winter Pruning', icon: '✂️', label: 'Winter Pruning' },
        { value: 'Scab Disease Control', icon: '🦠', label: 'Scab Disease Control' },
        { value: 'Codling Moth Spray', icon: '🐛', label: 'Codling Moth Spray' },
        { value: 'Fruit Thinning', icon: '🍎', label: 'Fruit Thinning' },
        { value: 'Mulching Around Base', icon: '🍂', label: 'Mulching Around Base' },
        { value: 'Harvesting at Color Break', icon: '🍎', label: 'Harvesting at Color Break' }
    ],
    'banana': [
        { value: 'Pit Preparation with FYM', icon: '⛏️', label: 'Pit Preparation with FYM' },
        { value: 'Sucker Planting', icon: '🌱', label: 'Sucker Planting' },
        { value: 'Regular Watering', icon: '💧', label: 'Regular Watering' },
        { value: 'Monthly Fertilization', icon: '🧪', label: 'Monthly Fertilization' },
        { value: 'Desuckering', icon: '✂️', label: 'Desuckering' },
        { value: 'Panama Wilt Monitoring', icon: '🦠', label: 'Panama Wilt Monitoring' },
        { value: 'Weevil Control', icon: '🐛', label: 'Weevil Control' },
        { value: 'Propping Bunches', icon: '🪵', label: 'Propping Bunches' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Bunch Harvesting', icon: '🍌', label: 'Bunch Harvesting' }
    ],
    'grapes': [
        { value: 'Trench Preparation', icon: '⛏️', label: 'Trench Preparation' },
        { value: 'Cutting Plantation', icon: '🌱', label: 'Cutting Plantation' },
        { value: 'Drip Irrigation', icon: '💧', label: 'Drip Irrigation' },
        { value: 'Split Fertilizer Doses', icon: '🧪', label: 'Split Fertilizer Doses' },
        { value: 'Winter Pruning', icon: '✂️', label: 'Winter Pruning' },
        { value: 'Powdery Mildew Spray', icon: '🦠', label: 'Powdery Mildew Spray' },
        { value: 'Thrips Management', icon: '🐛', label: 'Thrips Management' },
        { value: 'Bunch Thinning', icon: '🍇', label: 'Bunch Thinning' },
        { value: 'Canopy Management', icon: '🍂', label: 'Canopy Management' },
        { value: 'Harvesting at Brix Level', icon: '🍇', label: 'Harvesting at Brix Level' }
    ],
    'mango': [
        { value: 'Large Pit Digging', icon: '⛏️', label: 'Large Pit Digging' },
        { value: 'Grafted Plant Setting', icon: '🌱', label: 'Grafted Plant Setting' },
        { value: 'Basin Irrigation', icon: '💧', label: 'Basin Irrigation' },
        { value: 'Annual Fertilization', icon: '🧪', label: 'Annual Fertilization' },
        { value: 'Post-harvest Pruning', icon: '✂️', label: 'Post-harvest Pruning' },
        { value: 'Anthracnose Control', icon: '🦠', label: 'Anthracnose Control' },
        { value: 'Hopper & Fruit Fly Spray', icon: '🐛', label: 'Hopper & Fruit Fly Spray' },
        { value: 'Fruit Thinning', icon: '🥭', label: 'Fruit Thinning' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Harvesting with Stalk', icon: '🥭', label: 'Harvesting with Stalk' }
    ],
    'muskmelon': [
        { value: 'Raised Bed Preparation', icon: '⛏️', label: 'Raised Bed Preparation' },
        { value: 'Direct Seeding in Pits', icon: '🌱', label: 'Direct Seeding in Pits' },
        { value: 'Frequent Light Irrigation', icon: '💧', label: 'Frequent Light Irrigation' },
        { value: 'NPK in Splits', icon: '🧪', label: 'NPK in Splits' },
        { value: 'Vine Training', icon: '🌿', label: 'Vine Training' },
        { value: 'Downy Mildew Control', icon: '🦠', label: 'Downy Mildew Control' },
        { value: 'Fruit Fly Traps', icon: '🐛', label: 'Fruit Fly Traps' },
        { value: 'Hand Pollination', icon: '🐝', label: 'Hand Pollination' },
        { value: 'Straw Mulching', icon: '🍂', label: 'Straw Mulching' },
        { value: 'Slip Test Harvesting', icon: '🍈', label: 'Slip Test Harvesting' }
    ],
    'orange': [
        { value: 'Pit Preparation', icon: '⛏️', label: 'Pit Preparation' },
        { value: 'Budded Sapling Planting', icon: '🌱', label: 'Budded Sapling Planting' },
        { value: 'Regular Watering', icon: '💧', label: 'Regular Watering' },
        { value: 'Fertilizer in Circles', icon: '🧪', label: 'Fertilizer in Circles' },
        { value: 'Pruning Dead Wood', icon: '✂️', label: 'Pruning Dead Wood' },
        { value: 'Citrus Canker Spray', icon: '🦠', label: 'Citrus Canker Spray' },
        { value: 'Psyllid Control', icon: '🐛', label: 'Psyllid Control' },
        { value: 'Fruit Drop Prevention', icon: '🍊', label: 'Fruit Drop Prevention' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Color-based Harvesting', icon: '🍊', label: 'Color-based Harvesting' }
    ],
    'papaya': [
        { value: 'Pit Filling with Compost', icon: '⛏️', label: 'Pit Filling with Compost' },
        { value: 'Seedling Transplanting', icon: '🌱', label: 'Seedling Transplanting' },
        { value: 'Daily Watering', icon: '💧', label: 'Daily Watering' },
        { value: 'Monthly Fertilization', icon: '🧪', label: 'Monthly Fertilization' },
        { value: 'Male Plant Removal', icon: '✂️', label: 'Male Plant Removal' },
        { value: 'Ringspot Virus Check', icon: '🦠', label: 'Ringspot Virus Check' },
        { value: 'Mealybug Control', icon: '🐛', label: 'Mealybug Control' },
        { value: 'Stem Support', icon: '🪵', label: 'Stem Support' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Color Change Harvesting', icon: '🍈', label: 'Color Change Harvesting' }
    ],
    'pomegranate': [
        { value: 'Pit Digging', icon: '⛏️', label: 'Pit Digging' },
        { value: 'Cutting/Sapling Planting', icon: '🌱', label: 'Cutting/Sapling Planting' },
        { value: 'Drip Irrigation', icon: '💧', label: 'Drip Irrigation' },
        { value: 'Fertilizer Application', icon: '🧪', label: 'Fertilizer Application' },
        { value: 'Sucker Removal', icon: '✂️', label: 'Sucker Removal' },
        { value: 'Bacterial Blight Spray', icon: '🦠', label: 'Bacterial Blight Spray' },
        { value: 'Fruit Borer Control', icon: '🐛', label: 'Fruit Borer Control' },
        { value: 'Fruit Bagging', icon: '🎒', label: 'Fruit Bagging' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Sound Test Harvesting', icon: '🍎', label: 'Sound Test Harvesting' }
    ],
    'watermelon': [
        { value: 'Bed Preparation', icon: '⛏️', label: 'Bed Preparation' },
        { value: 'Pit Sowing', icon: '🌱', label: 'Pit Sowing' },
        { value: 'Regular Irrigation', icon: '💧', label: 'Regular Irrigation' },
        { value: 'Fertilizer in Splits', icon: '🧪', label: 'Fertilizer in Splits' },
        { value: 'Vine Training', icon: '🌿', label: 'Vine Training' },
        { value: 'Fusarium Wilt Check', icon: '🦠', label: 'Fusarium Wilt Check' },
        { value: 'Aphid & Fruit Fly Control', icon: '🐛', label: 'Aphid & Fruit Fly Control' },
        { value: 'Pollination Check', icon: '🐝', label: 'Pollination Check' },
        { value: 'Straw Mulching', icon: '🍂', label: 'Straw Mulching' },
        { value: 'Thump Test Harvesting', icon: '🍉', label: 'Thump Test Harvesting' }
    ],
    'coconut': [
        { value: 'Large Pit Digging', icon: '⛏️', label: 'Large Pit Digging' },
        { value: 'Seedling Planting', icon: '🌱', label: 'Seedling Planting' },
        { value: 'Regular Watering', icon: '💧', label: 'Regular Watering' },
        { value: 'Annual Fertilization', icon: '🧪', label: 'Annual Fertilization' },
        { value: 'Frond Cutting', icon: '✂️', label: 'Frond Cutting' },
        { value: 'Bud Rot Monitoring', icon: '🦠', label: 'Bud Rot Monitoring' },
        { value: 'Rhinoceros Beetle Trap', icon: '🐛', label: 'Rhinoceros Beetle Trap' },
        { value: 'Button Stage Check', icon: '🥥', label: 'Button Stage Check' },
        { value: 'Basin Mulching', icon: '🍂', label: 'Basin Mulching' },
        { value: 'Mature Nut Harvesting', icon: '🥥', label: 'Mature Nut Harvesting' }
    ],

    // COMMERCIAL CROPS
    'cotton': [
        { value: 'Deep Plowing', icon: '🚜', label: 'Deep Plowing' },
        { value: 'Seed Treatment & Sowing', icon: '🌱', label: 'Seed Treatment & Sowing' },
        { value: 'Thinning & Gap Filling', icon: '🌿', label: 'Thinning & Gap Filling' },
        { value: 'Critical Stage Irrigation', icon: '💧', label: 'Critical Stage Irrigation' },
        { value: 'Split Fertilizer Doses', icon: '🧪', label: 'Split Fertilizer Doses' },
        { value: 'Weeding & Intercultivation', icon: '🌿', label: 'Weeding & Intercultivation' },
        { value: 'Bollworm Management', icon: '🐛', label: 'Bollworm Management' },
        { value: 'Topping', icon: '✂️', label: 'Topping' },
        { value: 'Boll Opening Check', icon: '☁️', label: 'Boll Opening Check' },
        { value: 'Multiple Pickings', icon: '☁️', label: 'Multiple Pickings' }
    ],
    'jute': [
        { value: 'Land Preparation', icon: '🚜', label: 'Land Preparation' },
        { value: 'Broadcasting Seeds', icon: '🌱', label: 'Broadcasting Seeds' },
        { value: 'Thinning Plants', icon: '🌿', label: 'Thinning Plants' },
        { value: 'Regular Irrigation', icon: '💧', label: 'Regular Irrigation' },
        { value: 'Top Dressing Urea', icon: '🧪', label: 'Top Dressing Urea' },
        { value: 'Weeding', icon: '🌿', label: 'Weeding' },
        { value: 'Stem Rot Control', icon: '🦠', label: 'Stem Rot Control' },
        { value: 'Flowering Stage Check', icon: '🌼', label: 'Flowering Stage Check' },
        { value: 'Harvesting at Flowering', icon: '⚙️', label: 'Harvesting at Flowering' },
        { value: 'Retting Process', icon: '💧', label: 'Retting Process' }
    ],
    'coffee': [
        { value: 'Pit Preparation', icon: '⛏️', label: 'Pit Preparation' },
        { value: 'Seedling Transplanting', icon: '🌱', label: 'Seedling Transplanting' },
        { value: 'Shade Management', icon: '🌳', label: 'Shade Management' },
        { value: 'Drip/Sprinkler Irrigation', icon: '💧', label: 'Drip/Sprinkler Irrigation' },
        { value: 'Fertilizer in Splits', icon: '🧪', label: 'Fertilizer in Splits' },
        { value: 'Pruning & Training', icon: '✂️', label: 'Pruning & Training' },
        { value: 'Leaf Rust Spray', icon: '🦠', label: 'Leaf Rust Spray' },
        { value: 'White Stem Borer Control', icon: '🐛', label: 'White Stem Borer Control' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Cherry Picking', icon: '☕', label: 'Cherry Picking' }
    ],
    'tea': [
        { value: 'Terrace Preparation', icon: '⛏️', label: 'Terrace Preparation' },
        { value: 'Cutting Plantation', icon: '🌱', label: 'Cutting Plantation' },
        { value: 'Shade Tree Planting', icon: '🌳', label: 'Shade Tree Planting' },
        { value: 'Regular Irrigation', icon: '💧', label: 'Regular Irrigation' },
        { value: 'Fertilizer Application', icon: '🧪', label: 'Fertilizer Application' },
        { value: 'Pruning Cycles', icon: '✂️', label: 'Pruning Cycles' },
        { value: 'Blister Blight Control', icon: '🦠', label: 'Blister Blight Control' },
        { value: 'Tea Mosquito Bug Spray', icon: '🐛', label: 'Tea Mosquito Bug Spray' },
        { value: 'Mulching', icon: '🍂', label: 'Mulching' },
        { value: 'Leaf Plucking (2 leaves + bud)', icon: '🍃', label: 'Leaf Plucking (2 leaves + bud)' }
    ]
};

// Get crop-specific tasks
function getCropTasks(crop) {
    if (!crop) return [];
    const cropLower = crop.toLowerCase().trim();

    // Direct match
    if (cropSpecificTasks[cropLower]) {
        return cropSpecificTasks[cropLower];
    }

    // Fuzzy match
    for (const [key, tasks] of Object.entries(cropSpecificTasks)) {
        if (cropLower.includes(key) || key.includes(cropLower)) {
            return tasks;
        }
    }

    // Default fallback tasks
    return [
        { value: 'Land Preparation', icon: '🚜', label: 'Land Preparation' },
        { value: 'Sowing/Planting', icon: '🌱', label: 'Sowing/Planting' },
        { value: 'Irrigation', icon: '💧', label: 'Irrigation' },
        { value: 'Fertilization', icon: '🧪', label: 'Fertilization' },
        { value: 'Weeding', icon: '🌿', label: 'Weeding' },
        { value: 'Pest Control', icon: '🐛', label: 'Pest Control' },
        { value: 'Disease Management', icon: '🦠', label: 'Disease Management' },
        { value: 'Harvesting', icon: '🌾', label: 'Harvesting' },
        { value: 'Post-Harvest', icon: '📦', label: 'Post-Harvest' },
        { value: 'Other', icon: '📋', label: 'Other' }
    ];
}

// Populate task dropdown based on specific crop
function populateTaskDropdown() {
    const tasks = getCropTasks(cropName);
    const taskSelect = document.getElementById('taskType');

    // Clear existing options
    if (taskSelect) {
        taskSelect.innerHTML = '<option value="">Select Task Type</option>';

        // Add crop-specific tasks
        tasks.forEach(task => {
            const option = document.createElement('option');
            option.value = task.value;
            option.textContent = `${task.icon} ${task.label}`;
            taskSelect.appendChild(option);
        });
    }

    console.log(`✅ Loaded ${tasks.length} crop-specific tasks for: ${cropName}`);
}

// Load tasks from localStorage on page load
document.addEventListener('DOMContentLoaded', function () {
    // Populate task dropdown based on crop category
    populateTaskDropdown();

    loadTasks();
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    const taskDateInput = document.getElementById('taskDate');
    if (taskDateInput) {
        taskDateInput.min = today;
    }

    // Set minimum sowing date for harvest planner
    const sowingDateInput = document.getElementById('plannerSowingDate');
    if (sowingDateInput) {
        sowingDateInput.min = today;
        sowingDateInput.value = today; // Set default to today
    }
});

// Start Monitoring Crop - Save to Database
function startMonitoringCrop() {
    const tasks = JSON.parse(localStorage.getItem(storageKey) || '[]');
    const harvestPlan = JSON.parse(localStorage.getItem(`harvestPlan_${cropName}`) || '{}');

    if (tasks.length === 0 && !harvestPlan.sowingDate) {
        if (!confirm('You haven\'t added any tasks or harvest plan yet. Do you still want to start monitoring?')) {
            return;
        }
    }

    // Calculate task completion percentage
    const completedTasks = tasks.filter(t => t.completed).length;
    const taskCompletionPercentage = tasks.length > 0 ? Math.round((completedTasks / tasks.length) * 100) : 0;

    // Prepare crop activity data
    const cropActivity = {
        crop: cropName,
        crop_display_name: cropName,
        tasks: tasks,
        harvest_plan: harvestPlan,
        task_completion: taskCompletionPercentage,
        total_tasks: tasks.length,
        completed_tasks: completedTasks,
        start_date: harvestPlan.sowingDate || new Date().toISOString().split('T')[0],
        duration_days: harvestPlan.duration || 90,
        expected_harvest_date: harvestPlan.harvestDate || null,
        current_stage: 'Planning',
        progress: 0,
        created_at: new Date().toISOString()
    };

    // Save to server
    fetch('/api/crop-activity/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(cropActivity)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Crop monitoring started successfully!', 'success');
                // Clear localStorage for this crop
                localStorage.removeItem(storageKey);
                localStorage.removeItem(`harvestPlan_${cropName}`);
                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    const dashboardUrl = document.body.dataset.dashboardUrl;
                    window.location.href = dashboardUrl;
                }, 1500);
            } else {
                showNotification('Failed to start monitoring: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error starting monitoring. Please try again.', 'error');
        });
}


// Harvest Plan Generation
function generateHarvestPlan() {
    const sowingDateInput = document.getElementById('plannerSowingDate');
    const durationInput = document.getElementById('plannerDuration');
    const cropInput = document.getElementById('plannerCrop');

    if (!sowingDateInput || !durationInput || !cropInput) return;

    const sowingDate = sowingDateInput.value;
    const duration = parseInt(durationInput.value);
    const crop = cropInput.value;

    if (!sowingDate) {
        showNotification('Please select a sowing date', 'error');
        return;
    }

    if (!duration || duration < 1) {
        showNotification('Please enter a valid growth duration', 'error');
        return;
    }

    // Calculate harvest date
    const sowingDateObj = new Date(sowingDate);
    const harvestDateObj = new Date(sowingDateObj);
    harvestDateObj.setDate(harvestDateObj.getDate() + duration);

    // Format dates
    const sowingFormatted = sowingDateObj.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
    const harvestFormatted = harvestDateObj.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });

    // Calculate weeks
    const weeks = Math.floor(duration / 7);
    const days = duration % 7;
    const durationText = weeks > 0
        ? `${weeks} week${weeks > 1 ? 's' : ''}${days > 0 ? ` and ${days} day${days > 1 ? 's' : ''}` : ''}`
        : `${days} day${days > 1 ? 's' : ''}`;

    // Display result
    const resultDiv = document.getElementById('harvestPlanResult');
    const detailsDiv = document.getElementById('harvestPlanDetails');

    if (detailsDiv) {
        detailsDiv.innerHTML = `
            <div style="margin-bottom: 8px;">
                <strong>Crop:</strong> ${crop}
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Sowing Date:</strong> ${sowingFormatted}
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Growth Duration:</strong> ${durationText} (${duration} days)
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Expected Harvest Date:</strong> <span style="font-weight: 700; color: #059669;">${harvestFormatted}</span>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #bbf7d0; font-size: 13px;">
                <i class="fas fa-info-circle"></i> Mark your calendar! Your ${crop} should be ready for harvest around ${harvestFormatted}.
            </div>
        `;
    }

    if (resultDiv) {
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    showNotification('Harvest plan generated successfully!', 'success');

    // Save harvest plan to localStorage
    const harvestPlan = {
        crop: crop,
        sowingDate: sowingDate,
        duration: duration,
        harvestDate: harvestDateObj.toISOString().split('T')[0],
        createdAt: new Date().toISOString()
    };
    localStorage.setItem(`harvestPlan_${crop}`, JSON.stringify(harvestPlan));

    // Logic implementation: Auto-add fundamental tasks to timeline
    autoAddFundamentalTasks(crop, sowingDate, harvestPlan.harvestDate);
}

/**
 * Automatically adds fundamental tasks like Sowing and Harvesting 
 * to the timeline when a harvest plan is generated.
 */
/**
 * Automatically adds fundamental tasks like Sowing and Harvesting 
 * to the timeline when a harvest plan is generated.
 * Ensures no duplicate Sowing/Harvesting tasks exist, replacing old ones if necessary.
 */
function autoAddFundamentalTasks(crop, sowingDate, harvestDate) {
    let tasks = JSON.parse(localStorage.getItem(storageKey) || '[]');
    let updated = false;

    const fundamentalTasks = [
        { type: 'Sowing/Planting', date: sowingDate, description: 'Initial sowing based on harvest plan.' },
        { type: 'Harvesting', date: harvestDate, description: 'Expected harvest date.' }
    ];

    // Remove existing fundamental tasks to avoid duplicates/confusion if plan is regenerated
    const previousLength = tasks.length;
    tasks = tasks.filter(t => !['Sowing/Planting', 'Harvesting'].includes(t.type));

    if (tasks.length !== previousLength) {
        updated = true; // Mark updated if we removed something
    }

    fundamentalTasks.forEach(ft => {
        tasks.push({
            id: Date.now() + Math.random(), // Unique ID
            type: ft.type,
            date: ft.date,
            description: ft.description,
            cropName: cropName,
            completed: false,
            createdAt: new Date().toISOString()
        });
        updated = true;
    });

    if (updated) {
        localStorage.setItem(storageKey, JSON.stringify(tasks));
        loadTasks();
        showNotification('Timeline updated with harvest plan dates!', 'success');
    }
}


function addTask(event) {
    if (event) event.preventDefault();

    const taskTypeInput = document.getElementById('taskType');
    const taskDateInput = document.getElementById('taskDate');
    const taskDescriptionInput = document.getElementById('taskDescription');

    if (!taskTypeInput || !taskDateInput) return;

    const taskType = taskTypeInput.value;
    const taskDate = taskDateInput.value;
    const taskDescription = taskDescriptionInput ? taskDescriptionInput.value : '';

    if (!taskType || !taskDate) {
        showNotification('Please fill in task type and date', 'error');
        return;
    }

    let tasks = JSON.parse(localStorage.getItem(storageKey) || '[]');

    // 1. Strict Check: Fundamental tasks generally happen once per crop cycle.
    // Warn if adding a second Sowing or Harvesting date.
    if (['Sowing/Planting', 'Harvesting'].includes(taskType)) {
        const existingFundamental = tasks.find(t => t.type === taskType);
        if (existingFundamental) {
            if (!confirm(`A '${taskType}' task already exists on ${formatDate(existingFundamental.date)}. Do you want to add another one?`)) {
                return;
            }
        }
    }

    // 2. Exact Duplicate Check: Same type on same date
    const isDuplicate = tasks.some(t => t.type.toLowerCase() === taskType.toLowerCase() && t.date === taskDate);

    if (isDuplicate) {
        showNotification('This task is already scheduled for this date!', 'warning');
        return;
    }

    const task = {
        id: Date.now() + Math.floor(Math.random() * 1000), // More unique ID
        type: taskType,
        date: taskDate,
        description: taskDescription,
        cropName: cropName,
        completed: false,
        createdAt: new Date().toISOString()
    };

    // Save to localStorage
    tasks.push(task);
    localStorage.setItem(storageKey, JSON.stringify(tasks));

    // Save to server
    saveTaskToServer(task);

    // Reset form
    const taskForm = document.getElementById('taskForm');
    if (taskForm) taskForm.reset();

    // Reload tasks display
    loadTasks();

    // Show success message
    showNotification('Task added successfully!', 'success');
}

function loadTasks() {
    const tasks = JSON.parse(localStorage.getItem(storageKey) || '[]');
    const taskItems = document.getElementById('taskItems');

    if (!taskItems) return;

    if (tasks.length === 0) {
        taskItems.innerHTML = '<div class="empty-tasks"><i class="fas fa-calendar-times"></i><br>No tasks scheduled yet. Add your first task above!</div>';
        return;
    }

    // Sort tasks by date
    tasks.sort((a, b) => new Date(a.date) - new Date(b.date));

    taskItems.innerHTML = tasks.map(task => {
        const taskIcon = getTaskIcon(task.type);
        const formattedDate = formatDate(task.date);

        return `
            <div class="task-item">
                <div class="task-info">
                    <div class="task-type">${taskIcon} ${task.type}</div>
                    <div class="task-date">
                        <i class="fas fa-calendar"></i> ${formattedDate}
                    </div>
                    ${task.description ? `<div class="task-desc">${task.description}</div>` : ''}
                </div>
                <button class="task-delete" onclick="deleteTask(${task.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
    }).join('');
}

function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    let tasks = JSON.parse(localStorage.getItem(storageKey) || '[]');
    tasks = tasks.filter(task => task.id !== taskId);
    localStorage.setItem(storageKey, JSON.stringify(tasks));

    // Delete from server
    deleteTaskFromServer(taskId);

    loadTasks();
    showNotification('Task deleted successfully!', 'error');
}

function getTaskIcon(taskType) {
    // 1. First check if it's one of the basic/standard tasks
    const standardIcons = {
        'Sowing': '🌱',
        'Sowing/Planting': '🌱',
        'Irrigation': '💧',
        'Fertilization': '🧪',
        'Weeding': '🌿',
        'Pest Control': '🐛',
        'Pruning': '✂️',
        'Harvesting': '🌾',
        'Harvesting at Maturity': '🌾',
        'Soil Testing': '🔬',
        'Land Preparation': '🚜',
        'Other': '📋'
    };

    if (standardIcons[taskType]) return standardIcons[taskType];

    // 2. Check current crop's specific tasks for an icon
    const currentCropTasks = getCropTasks(cropName);
    const specificTask = currentCropTasks.find(t => t.value === taskType || t.label === taskType);

    if (specificTask && specificTask.icon) {
        return specificTask.icon;
    }

    // 3. Fallback to generic icon
    return '📋';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
}

function saveTaskToServer(task) {
    fetch('/api/tasks/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(task)
    })
        .then(response => response.json())
        .then(data => console.log('Task saved to server:', data))
        .catch(error => console.error('Error saving task:', error));
}

function deleteTaskFromServer(taskId) {
    fetch(`/api/tasks/delete/${taskId}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => console.log('Task deleted from server:', data))
        .catch(error => console.error('Error deleting task:', error));
}

function showNotification(message, type) {
    if (window.showToast) {
        window.showToast(message, type);
        return;
    }

    // Fallback if main.js isn't loaded
    const notification = document.createElement('div');
    const color = type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#f59e0b');

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
        font-family: system-ui, -apple-system, sans-serif;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Export tasks for dashboard display
function getAllTasks() {
    return JSON.parse(localStorage.getItem(storageKey) || '[]');
}
