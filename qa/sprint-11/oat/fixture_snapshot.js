
// Canonical Extended JSON snapshot of synthetic documents.
// Documents are sorted by collection and _id.

const name = process.env.OAT_DB;

if (!/^ineo_test_s11(?:_restore)?$/.test(name || "")) {
    throw Error("Invalid QA DB");
}

const d = db.getSiblingDB(name);
const collections = d.getCollectionNames().sort();

let total = 0;

for (const c of collections) {

    const collection = d.getCollection(c);

    print(EJSON.stringify({
        collection: c,
        count: collection.countDocuments({})
    }, { relaxed: false }));

    const documents = collection
        .find({})
        .sort({ _id: 1 })
        .toArray();

    for (const doc of documents) {

        print(EJSON.stringify(doc, {
            relaxed: false
        }));

        total++;
    }
}

if (total === 0) {
    throw Error("Empty synthetic fixture");
}
