module.exports = {
	globDirectory: 'html/',
	globPatterns: [
		'**/*.{css,ico,png,html,json,js}'
	],
	swDest: 'html/service-worker.js',
	maximumFileSizeToCacheInBytes: 5 * 1024 * 1024, // Limite augmentée à 5 Mo
 	ignoreURLParametersMatching: [
		/^utm_/,
		/^fbclid$/
	]
};