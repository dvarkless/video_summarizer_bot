import logging
from pathlib import Path

import numpy as np
from langchain.chains import (LLMChain, MapReduceDocumentsChain,
                              ReduceDocumentsChain, StuffDocumentsChain)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.cluster import KMeans

from src.setup_handler import get_handler

logger = logging.getLogger(__name__)
logger.addHandler(get_handler())


class MapReduceSplitter:
    compression_power = 0.7
    separators = [
        '\n\n',
        '\n',
        '\t',
        '. ',
        '? ',
        '! ',
    ]

    def __init__(self,
                 llm_provider,
                 embeddings_provider,
                 map_prompt,
                 reduce_prompt,
                 premap_prompts=None,
                 postmap_prompts=None,
                 postreduce_prompts=None,
                 window_len=2000,
                 window_overlap=300,
                 n_docs_theshold=10,
                 max_tokens=4000,
                 ) -> None:
        self._llm_provider = llm_provider
        self._embeddings_provider = embeddings_provider
        self.map_prompt = map_prompt
        self.reduce_prompt = reduce_prompt
        self.max_tokens = max_tokens
        self.n_docs_theshold = n_docs_theshold

        self.premap_prompts = premap_prompts or {}
        self.postmap_prompts = postmap_prompts or {}
        self.postreduce_prompts = postreduce_prompts or {}

        self.text_splitter = \
            RecursiveCharacterTextSplitter(separators=self.separators,
                                           chunk_size=window_len,
                                           chunk_overlap=window_overlap
                                           )

    @property
    def llm(self):
        if not hasattr(self, '_llm'):
            raise AttributeError("self.llm does not exist")
        return self._llm

    @property
    def embeddings(self):
        if not hasattr(self, '_embeddings'):
            raise AttributeError("self.embeddings does not exist")
        return self._embeddings

    @llm.setter
    def llm(self, val):
        if hasattr(self, '_embeddings'):
            raise AttributeError(
                "self.llm accessed without deleting self.embeddings")
        self._llm = val

    @embeddings.setter
    def embeddings(self, val):
        if hasattr(self, '_llm'):
            raise AttributeError(
                "self.embeddings accessed without deleting self.llm")
        self._embeddings = val

    def load_docs(self, doc_path):
        logger.info('Call: MapReduceSplitter.load_docs')
        doc_path = Path(doc_path)
        with open(doc_path, 'r') as f:
            text = f.read()
        documents = self.text_splitter.split_text(text)
        return documents

    def compress_docs(self, documents):
        logger.info('Call: MapReduceSplitter.compress_docs')

        doc_len = len(documents)
        if (doc_len <= self.n_docs_theshold):
            return documents

        logger.info('Compressing docs')
        with self._embeddings_provider as self.embeddings:
            vectors = self.embeddings.embed_documents(
                [x.page_content for x in documents])

            # As the text grows larger, the compressed text becomes smaller
            mul_coeff = (doc_len /
                         self.n_docs_theshold) ** self.compression_power
            num_clusters = int(doc_len*mul_coeff)
            selected_ids = self._closest_docs(vectors, num_clusters)
            selected_docs = [documents[doc_id] for doc_id in selected_ids]
        return selected_docs

    def _closest_docs(self, vectors, num_clusters):
        """Chooses the most precise clusters of info"""
        logger.info('Call: MapReduceSplitter._closest_docs')

        kmeans = KMeans(n_clusters=num_clusters).fit(vectors)
        closest_indices = []

        # Finds `num_clusters` unique documents
        for center in kmeans.cluster_centers_:
            distances = np.linalg.norm(
                vectors - center, axis=1)

            closest_index = np.argmin(distances)
            closest_indices.append(closest_index)
        return sorted(closest_indices)

    def get_main_chain(self):
        logger.info('Call: MapReduceSplitter.get_main_chain')

        map_chain = LLMChain(
            llm=self.llm,
            prompt=self.map_prompt,
        )
        reduce_chain = LLMChain(
            llm=self.llm,
            prompt=self.reduce_prompt,
        )
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain, document_variable_name="text"
        )
        reduce_documents_chain = ReduceDocumentsChain(
            combine_documents_chain=combine_documents_chain,
            token_max=self.max_tokens,
        )
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            # The variable name in the llm_chain to put the documents in
            input_key="docs",
            document_variable_name="text",
            # Return the results of the map steps in the output
            return_intermediate_steps=True,
        )
        return map_reduce_chain

    def iterate_chains(self, docs, prompts):
        logger.info('Call: MapReduceSplitter.iterate_chains')

        out = {}
        for name, prompt in prompts.items():
            out[name] = []
            premap_chain = LLMChain(
                llm=self.llm,
                prompt=prompt
            )
            for doc in docs:
                out[name].append(premap_chain.run(doc))
        return out

    # It could be used on reduce output, but it could also be a chapter
    def fix_titles(self, titles: list[str]):
        logger.info('Call: MapReduceSplitter.fix_titles')

        fixed_titles = []
        for title in titles:
            title = title.split(':\n')[-1]
            title = title.strip("\'\"")
            fixed_titles.append(title)
        return fixed_titles

    def fix_chapters(self, chapters: list[str]):
        logger.info('Call: MapReduceSplitter.fix_chapters')

        fixed_chapters = []
        for chapter in chapters:
            chapter = chapter.split(':\n')[-1]
            fixed_chapters.append(chapter)
        return fixed_chapters

    def run(self, doc_path, doc_name=None):
        logger.info('Call: MapReduceSplitter.run')
        out_dict = {}

        documents = self.load_docs(doc_path)
        documents = self.compress_docs(documents)
        with self._llm_provider as self.llm:
            if self.premap_prompts:
                out_dict |= self.iterate_chains(documents, self.premap_prompts)

            map_reduce_chain = self.get_main_chain()
            mr_input = {'docs': [Document(page_content=doc)
                                 for doc in documents]}
            map_reduce_dict = map_reduce_chain(mr_input)
            chapter_outs = map_reduce_dict['intermediate_steps']
            brief_description = map_reduce_dict['output_text']

            if self.postmap_prompts:
                out_dict |= self.iterate_chains(
                    chapter_outs, self.postmap_prompts)

            if self.postreduce_prompts:
                out_dict |= self.iterate_chains(
                    brief_description, self.postreduce_prompts)

            out_dict['chapters'] = self.fix_chapters(chapter_outs)
            out_dict['description'] = self.fix_chapters(brief_description)
            out_dict['title'] = doc_name or '{name}'
        return out_dict
