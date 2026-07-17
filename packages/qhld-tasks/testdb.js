conn = new Mongo();
db = conn.getDB("tipi");

db.alerts.deleteMany({});
db.alerts.insertMany([
    {
        "_id" : "4be4373d380234522242344322343422d2ad044e",
        "email" : "test@wadobo.com",
        "searches" : [
                {
                        "hash" : "51b96504da7b14121a860d9e6f75de2b7f1e2942",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[\"Acequia\"]}",
                        "created" : ISODate("2018-11-28T12:09:39.028Z"),
                        "validated" : false
                },
                {
                        "hash" : "c943451e8251a007342340bb097e820b91c7ac14",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[]}",
                        "created" : ISODate("2018-11-28T12:09:55.241Z"),
                        "validated" : false
                }
        ]
    },
    {
        "_id" : "4be4373d3802341231231aabd2343422d2ad044e",
        "email" : "test1@wadobo.com",
        "searches" : [
                {
                        "hash" : "51b96504da7b14121a860d9e6f75de2b7f1e2942",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[\"Acequia\"]}",
                        "created" : ISODate("2018-11-28T12:09:39.028Z"),
                        "validated" : false
                },
                {
                        "hash" : "c943451e8251a007342340bb097e820b91c7ac14",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[]}",
                        "created" : ISODate("2018-11-28T12:09:55.241Z"),
                        "validated" : true
                }
        ]
    },
    {
        "_id" : "4be43923478573849348344322343422d2ad044e",
        "email" : "test2@wadobo.com",
        "searches" : [
                {
                        "hash" : "51b96504da7b14121a860d9e6f75de2b7f1e2942",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[\"Acequia\"]}",
                        "created" : ISODate("2018-11-28T12:09:39.028Z"),
                        "validated" : true
                },
                {
                        "hash" : "c943451e8251a007342340bb097e820b91c7ac14",
                        "search" : "{\"topic\":\"ODS 6 - Agua limpia y saneamiento\",\"subtopics\":[\"6.1 Acceso universal al agua\"],\"tags\":[]}",
                        "created" : ISODate("2018-11-28T12:09:55.241Z"),
                        "validated" : true
                }
        ]
    }
]);
