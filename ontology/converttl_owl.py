from rdflib import Graph

g = Graph()
g.parse("./plo-measure-ontology.ttl", format="turtle")
g.serialize(destination="./plo-measure-ontology.owl", format="xml")