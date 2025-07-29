Mental Health Text Classification
=================================

The Mental Health Text Classification module provides AI-powered analysis of text to identify potential mental health categories. This tool can help users understand patterns in their thoughts and expressions, providing insights for better mental health awareness.

.. warning::
   This tool is for informational purposes only and is not a substitute for professional mental health care. If you're experiencing mental health concerns, please consult with a qualified healthcare provider.

Features
--------

* **AI-Powered Classification**: Uses a fine-tuned BERT model to classify text into 15 mental health categories
* **Fallback System**: Keyword-based classification when AI model is unavailable
* **Crisis Detection**: Automatic alerts for high-risk categories
* **History Tracking**: Complete history of all classifications with timestamps
* **Statistics**: Detailed analytics on classification patterns and trends
* **Privacy-First**: All data stored locally, no external transmission

Supported Categories
-------------------

The classifier can identify the following mental health categories:

**Mood Disorders**
  * ``depression`` - Depression and persistent sadness
  * ``bipolarreddit`` - Bipolar disorder and mood swings

**Anxiety Disorders**
  * ``anxiety`` - General anxiety and worry
  * ``socialanxiety`` - Social anxiety and social fears
  * ``healthanxiety`` - Health-related anxiety and hypochondria
  * ``ptsd`` - Post-traumatic stress disorder

**Neurodevelopmental**
  * ``adhd`` - Attention deficit hyperactivity disorder
  * ``autism`` - Autism spectrum conditions

**Personality Disorders**
  * ``bpd`` - Borderline personality disorder

**Substance-Related**
  * ``addiction`` - Substance or behavioral dependencies
  * ``alcoholism`` - Alcohol-related problems and dependencies

**Other Conditions**
  * ``schizophrenia`` - Schizophrenia and psychotic symptoms
  * ``EDAnonymous`` - Eating disorders and body image issues
  * ``lonely`` - Loneliness and social isolation

**Crisis Categories**
  * ``suicidewatch`` - Suicidal thoughts and crisis situations

Usage
-----

Basic Classification
~~~~~~~~~~~~~~~~~~~

Classify a single text string:

.. code-block:: bash

   om classify "I feel overwhelmed and anxious about everything lately"

Interactive Mode
~~~~~~~~~~~~~~~

Start an interactive classification session:

.. code-block:: bash

   om classify interactive

In interactive mode, you can:
- Enter text to classify
- Type ``history`` to see recent classifications
- Type ``stats`` to view category statistics
- Type ``quit`` to exit

View History
~~~~~~~~~~~

See your recent classifications:

.. code-block:: bash

   python3 mental_health_classifier.py history

View Statistics
~~~~~~~~~~~~~~

Get detailed statistics on your classification patterns:

.. code-block:: bash

   python3 mental_health_classifier.py stats

Test Mode
~~~~~~~~

Run the classifier with example texts:

.. code-block:: bash

   python3 mental_health_classifier.py test

Command Line Options
-------------------

The mental health classifier supports several command line options:

.. code-block:: bash

   python3 mental_health_classifier.py <command> [arguments]

Available commands:

* ``classify <text>`` - Classify the provided text
* ``interactive`` - Start interactive mode
* ``history [limit]`` - Show classification history (default: 10 entries)
* ``stats`` - Show category statistics
* ``test`` - Run with example texts

AI Model vs Fallback
--------------------

The classifier uses two methods:

**AI Model (Preferred)**
  * Uses ``tahaenesaslanturk/mental-health-classification-v0.1``
  * BERT-based neural network with 64% reported accuracy
  * Requires ``transformers`` and ``torch`` libraries
  * More nuanced and context-aware classification

**Keyword Fallback**
  * Uses pattern matching with mental health keywords
  * Works without additional dependencies
  * Faster but less sophisticated
  * Automatically used when AI model unavailable

Installation Requirements
------------------------

For full AI functionality, install additional dependencies:

.. code-block:: bash

   pip install -r requirements_classifier.txt

This includes:
- ``torch>=2.0.0`` - PyTorch for neural networks
- ``transformers>=4.30.0`` - Hugging Face transformers library
- ``accelerate>=0.20.0`` - Optional performance improvements

Crisis Detection
----------------

The classifier automatically detects high-risk categories and displays crisis resources:

**Critical Risk**
  * ``suicidewatch`` with >60% confidence

**High Risk**
  * ``depression`` or ``ptsd`` with >70% confidence

**Medium Risk**
  * ``anxiety`` or ``socialanxiety`` with >80% confidence

When high-risk categories are detected, the system displays:
- Crisis hotline numbers
- Emergency contact information
- Recommendations to seek professional help

Data Storage
-----------

All classification data is stored locally in ``~/.om/mental_health_classifier.db``:

**Classifications Table**
  * Individual text classifications with timestamps
  * Confidence scores and category predictions
  * User feedback and notes

**Category Statistics**
  * Count and average confidence per category
  * First and last detection timestamps
  * Trend analysis data

**Crisis Alerts**
  * High-risk classification alerts
  * Response tracking and acknowledgments

Privacy and Security
-------------------

* **Local Storage**: All data stored on your device only
* **No Transmission**: No data sent to external servers
* **User Control**: Complete control over your data
* **Encryption**: Database can be encrypted if needed

The classifier respects user privacy by:
- Never transmitting personal text data
- Storing all information locally
- Providing data export and deletion options
- Operating completely offline (except for initial model download)

Integration with om Platform
---------------------------

The mental health classifier integrates seamlessly with other om modules:

**Mood Tracking Integration**
  * Analyze mood journal entries
  * Correlate classifications with mood patterns
  * Enhanced mood insights

**Journal Analysis**
  * Classify journal entries automatically
  * Track emotional themes over time
  * Identify concerning patterns

**Crisis Support Integration**
  * Automatic alerts to rescue module
  * Enhanced crisis detection
  * Coordinated support responses

**Dashboard Integration**
  * Classification statistics in wellness dashboard
  * Trend visualization
  * Progress tracking

Accuracy and Limitations
-----------------------

**Model Accuracy**
  * AI model: ~64% accuracy (as reported by model author)
  * Keyword fallback: Variable, depends on text clarity
  * Best performance on clear, descriptive text

**Limitations**
  * Not a diagnostic tool
  * Cannot replace professional assessment
  * May misclassify ambiguous or complex text
  * Limited to English language text
  * Trained on Reddit data (may have biases)

**Best Practices**
  * Use for self-awareness and pattern recognition
  * Combine with professional mental health support
  * Consider context when interpreting results
  * Track patterns over time rather than single classifications

Examples
--------

**Depression Classification**

.. code-block:: bash

   $ om classify "I feel so hopeless and worthless, nothing matters anymore"
   
   🧠 Mental Health Classification
   ┌─────────────────────────────────────────────────────────────────┐
   │ depression                                                      │
   │ Confidence: 95.0%                                               │
   │ Depression and persistent sadness                               │
   │                                                                 │
   │ Method: Keyword-based classification                            │
   └─────────────────────────────────────────────────────────────────┘
   
   ⚠️  High-risk category detected. Please consider seeking professional help.

**Anxiety Classification**

.. code-block:: bash

   $ om classify "I'm having panic attacks and my heart races in social situations"
   
   🧠 Mental Health Classification
   ┌─────────────────────────────────────────────────────────────────┐
   │ socialanxiety                                                   │
   │ Confidence: 83.3%                                               │
   │ Social anxiety and social fears                                 │
   │                                                                 │
   │ Method: Keyword-based classification                            │
   └─────────────────────────────────────────────────────────────────┘

**Statistics View**

.. code-block:: bash

   $ python3 mental_health_classifier.py stats
   
   📊 Mental Health Category Statistics
   ┌───────────────┬───────┬────────────────┬─────────────────────┐
   │ Category      │ Count │ Avg Confidence │ Last Detected       │
   ├───────────────┼───────┼────────────────┼─────────────────────┤
   │ anxiety       │    10 │          50.0% │ 2025-07-27 08:54:58 │
   │ depression    │     4 │          95.0% │ 2025-07-27 08:54:52 │
   │ socialanxiety │     2 │          83.3% │ 2025-07-27 08:51:11 │
   └───────────────┴───────┴────────────────┴─────────────────────┘

Troubleshooting
--------------

**Model Loading Issues**

If you see "transformers library not available":

.. code-block:: bash

   pip install transformers torch

**Database Issues**

If classifications aren't saving:

.. code-block:: bash

   # Reinitialize database
   rm ~/.om/mental_health_classifier.db
   sqlite3 ~/.om/mental_health_classifier.db < mental_health_classifier_schema.sql

**Performance Issues**

For faster classification:

.. code-block:: bash

   # Install acceleration libraries
   pip install accelerate

**Memory Issues**

If running out of memory with AI model:
- Use keyword fallback mode (automatic when model fails)
- Close other applications
- Consider using a machine with more RAM

Future Enhancements
------------------

Planned improvements include:

* **Multi-language Support**: Support for languages beyond English
* **Custom Categories**: User-defined classification categories
* **Improved Accuracy**: Fine-tuning on more diverse datasets
* **Real-time Analysis**: Live analysis of typing patterns
* **Integration APIs**: Connect with external mental health platforms
* **Advanced Analytics**: Machine learning insights on personal patterns
* **Collaborative Features**: Anonymous pattern sharing for research

Contributing
-----------

To contribute to the mental health classifier:

1. **Data Collection**: Help improve keyword patterns
2. **Model Training**: Contribute to model fine-tuning
3. **Testing**: Test with diverse text samples
4. **Documentation**: Improve user guides and examples
5. **Integration**: Develop connections with other om modules

See the main om repository for contribution guidelines.

Support
-------

For support with the mental health classifier:

* **Technical Issues**: Check the om GitHub repository
* **Mental Health Crisis**: Contact emergency services or crisis hotlines
* **General Questions**: Use the om community forums

Remember: This tool is designed to support your mental health journey, not replace professional care. Always consult with qualified healthcare providers for mental health concerns.
