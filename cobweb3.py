import math
from random import normalvariate
from random import choice
from random import random
from cobweb import CobwebTree

class Cobweb3Tree(CobwebTree):

    #acuity = 1.0
    acuity = 1.0 / math.sqrt(2.0 * math.pi)
    #acuity = 0.5
    #acuity = 0.0000001

    def _unbiased_std(self, sample):
        if len(sample) == 1:
            return self.acuity

        mean = self._mean(sample)
        c4n = 1.0
        if len(sample) < 30:
            c4n = (math.sqrt(2.0 / (len(sample) - 1)) *
                   (math.gamma(len(sample)/2.0) /
                    math.gamma((len(sample) - 1)/2.0)))
        std = (math.sqrt(sum([(x - mean) * (x - mean) for x in
                              sample]) / (len(sample) - 1))
               * c4n)

        if std < self.acuity:
            std = self.acuity

        return std

    def _expected_correct_guesses(self):
        """
        Computes the number of attribute values that would be correctly guessed
        in the current concept. This extension supports both nominal and
        numeric attribute values. The acuity parameter should be set based on
        the domain cobweb is being used on. The acuity is set as a global
        parameter now. 
        """
        correct_guesses = 0.0

        for attr in self.av_counts:
            float_values = []
            for val in self.av_counts[attr]:
                if isinstance(val, float):
                    float_values += [val] * int(self.av_counts[attr][val])
                else:
                    prob = ((1.0 * self.av_counts[attr][val]) / self.count)
                    correct_guesses += (prob * prob)

            if len(float_values) == 0:
                continue

            std = self._unbiased_std(float_values)

            correct_guesses += (1.0 / (2.0 * math.sqrt(math.pi) * std))

        return correct_guesses

    def _pretty_print(self, depth=0):
        """
        Prints the categorization tree.
        """
        ret = str(('\t' * depth) + "|-")

        attributes = []

        for attr in self.av_counts:
            float_values = []
            values = []

            for val in self.av_counts[attr]:
                if isinstance(val, float):
                    float_values.append(val)
                else:
                    values.append("'" + str(val) + "': " +
                                  str(self.av_counts[attr][val]))

            if float_values:
                values.append("'mean':" + str(self._mean(float_values)))
                values.append("'std':" + str(self._std(float_values)))

            attributes.append("'" + attr + "': {" + ", ".join(values) + "}")
                  
        ret += "{" + ", ".join(attributes) + "}: " + str(self.count) + '\n'
        
        for c in self.children:
            ret += c._pretty_print(depth+1)

        return ret

    def predict(self, instance):
        """
        Given an instance predict any missing attribute values without
        modifying the tree. This has been modified to make predictions about
        nominal and numeric attribute values. 
        """
        prediction = {}

        # make a copy of the instance
        for attr in instance:
            prediction[attr] = instance[attr]

        concept = self._cobweb_categorize(instance)
        
        for attr in concept.av_counts:
            if attr in prediction:
                continue
            
            nominal_values = []
            float_values = []

            for val in concept.av_counts[attr]:
                if isinstance(val, float):
                    float_values += [val] * concept.av_counts[attr][val]
                else:
                    nominal_values += [val] * concept.av_counts[attr][val]

            if random() < ((len(nominal_values) * 1.0) / (len(nominal_values) +
                                                          len(float_values))):
                prediction[attr] = choice(nominal_values)
            else:
                prediction[attr] = normalvariate(self._mean(float_values),
                                                 self._std(float_values))

        return prediction

    def _get_probability(self, attr, val):
        """
        Gets the probability of a particular attribute value. This has been
        modified to support numeric and nominal values. The acuity is set as a
        global parameter now. 
        """
        if attr not in self.av_counts:
            return 0.<0

        if isinstance(val, float):
            float_values = []

            for av in self.av_counts[attr]:
                if isinstance(av, float):
                    float_values += [av] * self.av_counts[attr][av]

            mean = self._mean(float_values)
            std = self._unbiased_std(float_values)

            #print("get prob")
            #print("%0.2f, %0.2f (%0.2f)" % (val, mean, std))
            #print(((1.0 / (std * math.sqrt(2.0 * math.pi))) * 
            #        math.exp(-((val - mean) * (val - mean)) / (2.0 * std *
            #                                                   std))))

            #return ((1.0 / (std * math.sqrt(2.0 * math.pi))) * 
            #        math.exp(-((val - mean) * (val - mean)) / (2.0 * std * std)))

            # assign 100% accuracy to the mean
            return (math.exp(-((val - mean) * (val - mean)) / (2.0 * std * std)))
                                                                           
            # prob falling within interval from the mean.
            #point = abs((val - mean) / (std))
            #return 1.0 - (1.0 + math.erf((-1.0 * point) / math.sqrt(2)))#/2.0
        
        if val in self.av_counts[attr]:
            return (1.0 * self.av_counts[attr][val]) / self.count

        return 0.0

    def _output_json(self):
        """
        A modification of the cobweb output json to handle numeric values.
        """
        output = {}
        output['name'] = self.concept_name
        output['size'] = self.count
        output['children'] = []

        temp = {}
        for attr in self.av_counts:
            float_vals = []
            for value in self.av_counts[attr]:
                if isinstance(value, float):
                    float_vals.append(value)
                else:
                    temp[attr + " = " + str(value)] = self.av_counts[attr][value]
            if len(float_vals) > 0:
                mean = attr + "_mean = %0.2f (%0.2f)" % (self._mean(float_vals),
                                                self._unbiased_std(float_vals))
                temp[mean] = len(float_vals)

        for child in self.children:
            output['children'].append(child._output_json())

        output['counts'] = temp

        return output

if __name__ == "__main__":

    Cobweb3Tree().predictions("data_files/cobweb3_test2.json", 100, 20)
    #Cobweb3Tree().baseline_guesser("data_files/cobweb3_test.json", 30, 100)
    #print(Cobweb3Tree().cluster("cobweb3_test.json", 10, 1))


